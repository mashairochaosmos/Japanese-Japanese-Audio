import argparse
from google.cloud import texttospeech

# Gemini-TTSモデル
GEMINI_TTS_MODELS = {
    "gemini-2.5-pro-preview-tts": "Gemini 2.5 Pro プレビュー（最高品質・推奨）",
    "gemini-2.5-flash-preview-tts": "Gemini 2.5 Flash プレビュー（高速・低コスト）",
}

# Gemini-TTS話者（多言語対応、日本語でも使用可能）
GEMINI_TTS_SPEAKERS = [
    "Acherner", "Akiard", "Algenib", "Algieba", "Alnilam", "Aoede", "Autonoe",
    "Callirhoe", "Charon", "Despina", "Enceladus", "Erinome", "Fenrir",
    "Gacrux", "Iapetus", "Kore", "Laomedeia", "Larissa", "Mimas", "Nix",
    "Orus", "Phobos", "Proteus", "Rhea", "Styx", "Tethys", "Thalassa",
    "Thebe", "Titan", "Triton"
]

# 日本語用推奨話者
JAPANESE_RECOMMENDED_SPEAKERS = ["Kore", "Charon", "Callirhoe", "Aoede"]

# よく使う日本語ボイスのプリセット（従来のモデル）
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
    
    # Studio: 最高品質の音声（利用可能な場合）
    "studio_female": "ja-JP-Studio-B",      # 女性（Studioボイス）
    "studio_male": "ja-JP-Studio-C",        # 男性（Studioボイス）
}

def synthesize(
    text: str, 
    out_path: str = "output.mp3",
    voice_name: str = None,
    model_name: str = "gemini-2.5-pro-preview-tts",
    speaker: str = "Kore",
    prompt: str = None,
    language_code: str = "ja-JP",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    volume_gain_db: float = 0.0,
    sample_rate_hertz: int = 24000
):
    """
    テキストを音声に変換してファイルに保存
    
    Args:
        text: 音声化するテキスト
        out_path: 出力ファイルパス（デフォルト: output.mp3）
        voice_name: ボイス名（従来のモデル用、VOICE_PRESETSのキーも使用可能）
        model_name: Gemini-TTSモデル名（デフォルト: gemini-2.5-pro-preview-tts）
                    Noneの場合は従来のモデルを使用
        speaker: Gemini-TTS話者名（デフォルト: Charon）
        prompt: スタイル制御用の自然言語プロンプト（例: "友達とカジュアルに会話するように、親しみやすく面白おかしく話してください"）
        language_code: 言語コード（デフォルト: ja-JP）
        speaking_rate: 話速（0.25～4.0、デフォルト: 1.0、Gemini-TTSでは使用されない場合あり）
        pitch: ピッチ（-20.0～20.0セミトーン、デフォルト: 0.0、Gemini-TTSでは使用されない場合あり）
        volume_gain_db: 音量ゲイン（-96.0～16.0 dB、デフォルト: 0.0）
        sample_rate_hertz: サンプリングレート（8000, 16000, 22050, 24000, 32000, 44100, 48000）
                          デフォルト: 24000（高品質）
    """
    # クライアントを作成（プロジェクトIDは環境変数やgcloudの設定から自動検出される）
    client = texttospeech.TextToSpeechClient()
    
    # Gemini-TTSモデルを使用する場合
    if model_name and model_name in GEMINI_TTS_MODELS:
        print(f"Using Gemini-TTS model: {model_name} ({GEMINI_TTS_MODELS[model_name]})")
        
        # デフォルトプロンプト（日本語用）
        if prompt is None:
            if language_code == "ja-JP":
                prompt = "自然で親しみやすく、明るいトーンで日本語を話してください。"
            else:
                prompt = "Say the following in a natural and friendly way."
        
        # Gemini-TTS用の入力（textとpromptの両方を指定）
        input_text = texttospeech.SynthesisInput(text=text, prompt=prompt)
        
        # Gemini-TTS用のボイス設定
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=speaker,
            model_name=model_name
        )
        
        print(f"Speaker: {speaker}")
        print(f"Prompt: {prompt}")
        
    else:
        # 従来のモデルを使用
        if voice_name is None:
            voice_name = "neural2_female"
        
        # プリセット名が指定された場合は、実際のボイス名に変換
        if voice_name in VOICE_PRESETS:
            actual_voice_name = VOICE_PRESETS[voice_name]
            print(f"Using preset '{voice_name}': {actual_voice_name}")
        else:
            actual_voice_name = voice_name
        
        input_text = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=actual_voice_name,
        )
    
    # 高品質な音声設定
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
        pitch=pitch,
        volume_gain_db=volume_gain_db,
        sample_rate_hertz=sample_rate_hertz,
    )
    
    try:
        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config,
        )
        
        with open(out_path, "wb") as f:
            f.write(response.audio_content)
        
        if model_name and model_name in GEMINI_TTS_MODELS:
            print(f"Saved: {out_path} (Model: {model_name}, Speaker: {speaker})")
        else:
            print(f"Saved: {out_path} (Voice: {actual_voice_name})")
    
    except Exception as e:
        error_msg = str(e)
        if "Vertex AI API" in error_msg or "aiplatform.googleapis.com" in error_msg:
            print("\n" + "="*60)
            print("⚠️  Gemini-TTSを使用するには、Vertex AI APIを有効化する必要があります。")
            print("="*60)
            print("\n以下の手順で有効化してください：")
            print("1. Google Cloud Consoleにアクセス")
            print("2. Vertex AI APIを有効化:")
            print("   https://console.cloud.google.com/apis/library/aiplatform.googleapis.com")
            print("\nまたは、従来のモデルを使用してください：")
            print("  python main.py --text \"テキスト\" --model none --voice neural2_female")
            print("="*60)
        else:
            print(f"\nエラーが発生しました: {error_msg}")
        raise

def list_voices():
    """利用可能なボイスプリセットを表示"""
    print("\n利用可能なモデルとボイス:")
    print("=" * 60)
    print("\n【Gemini-TTS（最新・最高品質・推奨）】")
    print("  モデル:")
    for model, desc in GEMINI_TTS_MODELS.items():
        print(f"    {model}: {desc}")
    print("\n  話者（例）:")
    print(f"    {', '.join(GEMINI_TTS_SPEAKERS[:10])}...")
    print("    （全{}名）".format(len(GEMINI_TTS_SPEAKERS)))
    print("\n  特徴:")
    print("    - 自然言語プロンプトでスタイル、感情、トーンを制御可能")
    print("    - 最も自然で表現力の高い音声")
    print("    - プロンプト例: \"友達とカジュアルに会話するように、親しみやすく話してください\"")
    
    print("\n【従来のモデル（非推奨・互換性のため残存）】")
    print("  ※ Gemini 2.5 Pro TTSが推奨です")
    print("Standard（標準）:")
    print("  standard_female  - 女性 (ja-JP-Standard-A)")
    print("  standard_male    - 男性 (ja-JP-Standard-C)")
    print("\nWaveNet（自然で滑らか）:")
    print("  wavenet_female   - 女性 (ja-JP-Wavenet-A)")
    print("  wavenet_female2  - 女性 (ja-JP-Wavenet-C)")
    print("  wavenet_male     - 男性 (ja-JP-Wavenet-D)")
    print("\nNeural2（旧モデル）:")
    print("  neural2_female   - 女性 (ja-JP-Neural2-B)")
    print("  neural2_male     - 男性 (ja-JP-Neural2-C)")
    print("\nStudio（利用可能な場合）:")
    print("  studio_female    - 女性 (ja-JP-Studio-B)")
    print("  studio_male      - 男性 (ja-JP-Studio-C)")
    print("=" * 60)
    print("\n使用例:")
    print("  # Gemini 2.5 Pro TTS（デフォルト・最高品質・推奨）")
    print("  python main.py --text \"こんにちは\"")
    print("\n  # プロンプトでスタイルを指定")
    print("  python main.py --text \"こんにちは\" --prompt \"親しみやすく、明るいトーンで話してください\"")
    print("\n  # 話者を変更")
    print("  python main.py --text \"こんにちは\" --speaker Charon")
    print("\n  # 従来のモデルを使用（非推奨）")
    print("  python main.py --text \"こんにちは\" --model none --voice neural2_female")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Google Cloud Text-to-Speech API を使用してテキストを音声に変換",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # Gemini 2.5 Pro TTS（デフォルト・最高品質・推奨）
  python main.py --text "こんにちは"

  # プロンプトでスタイルを指定
  python main.py --text "こんにちは" --prompt "親しみやすく、明るいトーンで話してください"

  # 話者を変更
  python main.py --text "こんにちは" --speaker Kore

  # Gemini 2.5 Flash TTS（高速・低コスト）
  python main.py --text "こんにちは" --model gemini-2.5-flash-preview-tts

  # 従来のモデルを使用（非推奨）
  python main.py --text "こんにちは" --model none --voice neural2_female

  # 高品質設定（高サンプリングレート）
  python main.py --text "こんにちは" --sample-rate 48000

  # 出力ファイル名を指定
  python main.py --text "こんにちは" --out hello.mp3

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
        "--model", "-m",
        type=str,
        default="gemini-2.5-pro-preview-tts",
        choices=list(GEMINI_TTS_MODELS.keys()) + ["none"],
        help="Gemini-TTSモデル名（デフォルト: gemini-2.5-pro-preview-tts - 最高品質）"
             " 'none'を指定すると従来のモデルを使用"
    )
    
    parser.add_argument(
        "--speaker", "-s",
        type=str,
        default="Kore",
        help="Gemini-TTS話者名（デフォルト: Kore - 日本語推奨）"
    )
    
    parser.add_argument(
        "--prompt", "-pr",
        type=str,
        default=None,
        help="スタイル制御用の自然言語プロンプト（例: \"親しみやすく、明るいトーンで話してください\"）"
    )
    
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default=None,
        help="従来モデルのボイス名またはプリセット名（--model none の場合に使用）"
    )
    
    parser.add_argument(
        "--language", "-lang",
        type=str,
        default="ja-JP",
        help="言語コード（デフォルト: ja-JP）"
    )
    
    parser.add_argument(
        "--rate", "-r",
        type=float,
        default=1.0,
        help="話速（0.25～4.0、デフォルト: 1.0）"
    )
    
    parser.add_argument(
        "--pitch", "-p",
        type=float,
        default=0.0,
        help="ピッチ（-20.0～20.0セミトーン、デフォルト: 0.0）"
    )
    
    parser.add_argument(
        "--volume", "-vol",
        type=float,
        default=0.0,
        help="音量ゲイン（-96.0～16.0 dB、デフォルト: 0.0）"
    )
    
    parser.add_argument(
        "--sample-rate", "-sr",
        type=int,
        default=24000,
        choices=[8000, 16000, 22050, 24000, 32000, 44100, 48000],
        help="サンプリングレート（デフォルト: 24000 - 高品質）"
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
        model_name = None if args.model == "none" else args.model
        synthesize(
            text=args.text,
            out_path=args.out,
            voice_name=args.voice,
            model_name=model_name,
            speaker=args.speaker,
            prompt=args.prompt,
            language_code=args.language,
            speaking_rate=args.rate,
            pitch=args.pitch,
            volume_gain_db=args.volume,
            sample_rate_hertz=args.sample_rate
        )

