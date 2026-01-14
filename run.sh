#!/bin/bash
# 実行用スクリプト

cd /Users/masahiro.fukudome/Desktop/Japanese-Japanese-Audio

# 仮想環境をアクティベート
source .venv/bin/activate

# プロジェクトIDを環境変数に設定
export GOOGLE_CLOUD_PROJECT=japanese-japaneseaudio

# 実行
python main.py

