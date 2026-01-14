#!/bin/bash
# ADC（認証）設定用スクリプト

cd /Users/masahiro.fukudome/Desktop/Japanese-Japanese-Audio

# Google Cloud SDKのパスを追加
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# プロジェクトIDを設定（念のため）
gcloud config set project japanese-japaneseaudio

# ADCの設定（ブラウザが開いてGoogleログイン→許可）
echo "ブラウザが開きます。Googleアカウントでログインして許可してください..."
gcloud auth application-default login

echo ""
echo "認証が完了しました！"
echo "次に以下を実行してください:"
echo "  python main.py"
echo "または"
echo "  ./run.sh"

