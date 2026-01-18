import os
import glob

# プロジェクト内の bin フォルダを PATH に追加 (ffmpeg用)
# 親ディレクトリの bin フォルダを探す
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
bin_dir = os.path.join(project_root, "bin")
if os.path.exists(bin_dir):
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

from pydub import AudioSegment

def merge_audio_files(input_dir: str, output_file: str):
    """
    指定されたディレクトリ内のMP3ファイルを名前順に結合して保存する。
    
    Args:
        input_dir: 結合したいMP3ファイルが入っているディレクトリ (001.mp3, 002.mp3...)
        output_file: 結合後の出力ファイルパス
    """
    # MP3ファイルを取得してソート
    mp3_files = sorted(glob.glob(os.path.join(input_dir, "*.mp3")))
    
    if not mp3_files:
        print(f"Warning: No mp3 files found in {input_dir}")
        return False
        
    print(f"Merging {len(mp3_files)} files from {input_dir}...")
    
    combined = AudioSegment.empty()
    
    for mp3_file in mp3_files:
        # 結合済みのファイルが同じフォルダにある場合はスキップ
        if os.path.abspath(mp3_file) == os.path.abspath(output_file):
            continue
            
        try:
            audio = AudioSegment.from_mp3(mp3_file)
            combined += audio
        except Exception as e:
            print(f"Error reading {mp3_file}: {e}")
            return False
            
    try:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        combined.export(output_file, format="mp3")
        print(f"Saved combined audio: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving combined audio: {e}")
        # ffmpegがインストールされていない場合のヒント
        if "ffmpeg" in str(e).lower() or "file not found" in str(e).lower():
            print("Hint: ffmpeg might not be installed. Please install ffmpeg.")
            print("  macOS: brew install ffmpeg")
            print("  Ubuntu: sudo apt install ffmpeg")
        return False

if __name__ == "__main__":
    # テスト用
    import sys
    if len(sys.argv) < 3:
        print("Usage: python audio_merger.py <input_dir> <output_file>")
    else:
        merge_audio_files(sys.argv[1], sys.argv[2])
