import argparse
from google.cloud import texttospeech

# よく使う日本語ボイスのプリセット
VOICE_PRESETS = {
    # Standard（標準）: 少し機械的だが安い
    "standard_female": "ja-JP-Standard-A",  # 女性
    "standard_male": "ja-JP-Standard-C",    # 男性
    
    # WaveNet: 自然で滑らか
    "wavenet_female": "ja-JP-Wavenet-A",     # 女性
    "wavenet_female2": "ja-JP-Wavenet-C",   # 女性（別バリエーション）
    "wavenet_male": "ja-JP-Wavenet-D",      # 男性
    
    # Neural2: 非常に人間らしく表現力が高い
    "neural2_female": "ja-JP-Neural2-B",    # 女性
    "neural2_male": "ja-JP-Neural2-C",      # 男性
}

def synthesize(
    text: str, 
    out_path: str = "output.mp3",
    voice_name: str = "ja-JP-Wavenet-A"
):
    """
    テキストを音声に変換してファイルに保存
    
    Args:
        text: 音声化するテキスト
        out_path: 出力ファイルパス（デフォルト: output.mp3）
        voice_name: ボイス名（デフォルト: ja-JP-Wavenet-A）
                    VOICE_PRESETSのキー（例: "wavenet_female"）も使用可能
    """
    # クライアントを作成（プロジェクトIDは環境変数やgcloudの設定から自動検出される）
    client = texttospeech.TextToSpeechClient()
    
    input_text = texttospeech.SynthesisInput(text=text)
    
    # プリセット名が指定された場合は、実際のボイス名に変換
    if voice_name in VOICE_PRESETS:
        actual_voice_name = VOICE_PRESETS[voice_name]
        print(f"Using preset '{voice_name}': {actual_voice_name}")
    else:
        actual_voice_name = voice_name
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        name=actual_voice_name,
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config,
    )
    
    with open(out_path, "wb") as f:
        f.write(response.audio_content)
    
    print(f"Saved: {out_path} (Voice: {actual_voice_name})")

def list_voices():
    """利用可能なボイスプリセットを表示"""
    print("\n利用可能なボイスプリセット:")
    print("=" * 50)
    print("Standard（標準）:")
    print("  standard_female  - 女性 (ja-JP-Standard-A)")
    print("  standard_male    - 男性 (ja-JP-Standard-C)")
    print("\nWaveNet（自然で滑らか）:")
    print("  wavenet_female   - 女性 (ja-JP-Wavenet-A)")
    print("  wavenet_female2  - 女性 (ja-JP-Wavenet-C)")
    print("  wavenet_male     - 男性 (ja-JP-Wavenet-D)")
    print("\nNeural2（非常に人間らしい）:")
    print("  neural2_female   - 女性 (ja-JP-Neural2-B)")
    print("  neural2_male     - 男性 (ja-JP-Neural2-C)")
    print("=" * 50)
    print("\n直接ボイス名を指定することも可能です（例: ja-JP-Wavenet-A）")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Google Cloud Text-to-Speech API を使用してテキストを音声に変換",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使用（デフォルト: WaveNet女性）
  python main.py --text "こんにちは"

  # ボイスを指定
  python main.py --text "こんにちは" --voice neural2_female

  # 出力ファイル名を指定
  python main.py --text "こんにちは" --out hello.mp3 --voice wavenet_male

  # 利用可能なボイス一覧を表示
  python main.py --list-voices
        """
    )
    
    parser.add_argument(
        "--text", "-t",
        type=str,
        default="こんにちは。CursorからText-to-Speechを動かしています。",
        help="音声化するテキスト（デフォルト: サンプルテキスト）"
    )
    
    parser.add_argument(
        "--out", "-o",
        type=str,
        default="output.mp3",
        help="出力ファイルパス（デフォルト: output.mp3）"
    )
    
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="ja-JP-Wavenet-A",
        help="ボイス名またはプリセット名（デフォルト: ja-JP-Wavenet-A）"
    )
    
    parser.add_argument(
        "--list-voices", "-l",
        action="store_true",
        help="利用可能なボイスプリセット一覧を表示"
    )
    
    args = parser.parse_args()
    
    if args.list_voices:
        list_voices()
    else:
        synthesize(
            text=args.text,
            out_path=args.out,
            voice_name=args.voice
        )

