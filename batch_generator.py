import os
import argparse
import time
from glob import glob
from tqdm import tqdm
from google.cloud import texttospeech

# プロジェクト内の bin フォルダを PATH に追加 (ffmpeg用)
project_root = os.path.dirname(os.path.abspath(__file__))
bin_dir = os.path.join(project_root, "bin")
os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

from utils.text_splitter import split_text
from utils.audio_merger import merge_audio_files

# main.py から定数とロジックをインポートしたいが、
# main.py はスクリプトとして書かれている部分が多いので、必要な部分だけ再定義するか、
# main.py をリファクタリングするのが筋。
# ここでは簡易的に、必要な定数とクライアント初期化をここで行う。

# Gemini-TTSモデル
GEMINI_TTS_MODELS = {
    "gemini-2.5-pro-preview-tts": "Gemini 2.5 Pro プレビュー（最高品質・推奨）",
    "gemini-2.5-flash-preview-tts": "Gemini 2.5 Flash プレビュー（高速・低コスト）",
}

def synthesize_segment(
    client,
    text: str,
    out_path: str,
    model_name: str = "gemini-2.5-pro-preview-tts",
    speaker: str = "Kore",
    prompt: str = None,
    language_code: str = "ja-JP",
):
    """
    短いテキストセグメントを音声化して保存する
    """
    # デフォルトプロンプト
    if prompt is None:
        if language_code == "ja-JP":
            prompt = "自然で親しみやすく、明るいトーンで日本語を話してください。"
        else:
            prompt = "Say the following in a natural and friendly way."

    input_text = texttospeech.SynthesisInput(text=text, prompt=prompt)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=speaker,
        model_name=model_name
    )
    
    # 高品質設定（固定）
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        sample_rate_hertz=24000,
    )

    try:
        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config,
        )
        
        with open(out_path, "wb") as f:
            f.write(response.audio_content)
            
        return True
    
    except Exception as e:
        print(f"\nError synthesizing segment: {out_path}")
        print(f"Error details: {e}")
        return False

def process_book(
    book_dir: str,
    model_name: str = "gemini-2.5-pro-preview-tts",
    speaker: str = "Kore",
    prompt: str = None
):
    """
    本のディレクトリ構造を読み込んで一括変換する
    Structure:
      book_dir/
        raw/  <- テキストファイル (.txt)
        audio/ <- 出力先
    """
    raw_dir = os.path.join(book_dir, "raw")
    audio_output_dir = os.path.join(book_dir, "audio")
    
    if not os.path.exists(raw_dir):
        print(f"Error: raw directory not found at {raw_dir}")
        return

    os.makedirs(audio_output_dir, exist_ok=True)
    
    # テキストファイルを取得してソート
    txt_files = sorted(glob(os.path.join(raw_dir, "*.txt")))
    
    if not txt_files:
        print("No text files found in raw directory.")
        return

    print(f"Found {len(txt_files)} files. Starting processing...")
    
    client = texttospeech.TextToSpeechClient()

    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        file_base_name = os.path.splitext(filename)[0]
        
        print(f"\nProcessing: {filename}")
        
        with open(txt_file, "r", encoding="utf-8") as f:
            full_text = f.read()
            
        # テキスト分割
        chunks = split_text(full_text, max_chars=1500)
        print(f"  -> Split into {len(chunks)} chunks.")
        
        # 各チャンクを音声化
        # 出力フォルダ: audio/chapter_01/
        chapter_audio_dir = os.path.join(audio_output_dir, file_base_name)
        os.makedirs(chapter_audio_dir, exist_ok=True)
        
        for i, chunk in enumerate(tqdm(chunks, desc="Synthesizing")):
            # ファイル名: 001.mp3, 002.mp3 ...
            out_name = f"{i+1:03d}.mp3"
            out_path = os.path.join(chapter_audio_dir, out_name)
            
            # すでに存在する場合はスキップ（再開機能）
            if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                continue
            
            success = synthesize_segment(
                client=client,
                text=chunk,
                out_path=out_path,
                model_name=model_name,
                speaker=speaker,
                prompt=prompt
            )
            
            if not success:
                print("Stopping due to error.")
                return

            # レート制限回避のためのSleep
            time.sleep(1.0) 

        # 全チャンクの生成が完了したら結合
        print(f"  -> Merging audio files for {file_base_name}...")
        combined_output_path = os.path.join(audio_output_dir, f"{file_base_name}_combined.mp3")
        merge_audio_files(chapter_audio_dir, combined_output_path)

    print("\nProcessing complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process book text to audio")
    parser.add_argument("book_dir", help="Path to the book directory (must contain 'raw' folder)")
    parser.add_argument("--model", default="gemini-2.5-pro-preview-tts", help="Gemini TTS Model")
    parser.add_argument("--speaker", default="Kore", help="Speaker name")
    parser.add_argument("--prompt", default=None, help="Style prompt")
    
    args = parser.parse_args()
    
    process_book(
        book_dir=args.book_dir,
        model_name=args.model,
        speaker=args.speaker,
        prompt=args.prompt
    )
