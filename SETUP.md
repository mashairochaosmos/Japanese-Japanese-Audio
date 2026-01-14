# セットアップ手順

## 1. Google Cloud SDKのインストール

### macOSの場合：
1. 以下のURLからインストーラーをダウンロード：
   https://cloud.google.com/sdk/docs/install

2. ダウンロードした `.pkg` ファイルを実行してインストール

3. インストール後、ターミナルを再起動するか、以下を実行：
   ```bash
   source ~/.zshrc
   ```

## 2. ADC（Application Default Credentials）の設定

ターミナルで以下を実行：

```bash
# 現在のディレクトリに移動
cd /Users/masahiro.fukudome/Desktop/Japanese-Japanese-Audio

# 仮想環境をアクティベート
source .venv/bin/activate

# ADCの設定（ブラウザが開いてGoogleログイン→許可）
gcloud auth application-default login

# プロジェクトIDを設定（プロジェクトIDが分かっている場合）
# プロジェクトIDは Google Cloud Console で確認できます
gcloud config set project YOUR_PROJECT_ID
```

## 3. プロジェクトIDの確認方法

Google Cloud Console (https://console.cloud.google.com/) にアクセス：
- プロジェクト選択画面の上部に「プロジェクトID」が表示されます
- プロジェクト名「Japanese-JapaneseAudio」の場合、プロジェクトIDは通常：
  - `japanese-japaneseaudio`
  - `japanese-japanese-audio`
  などの形式（小文字、ハイフン含む）

## 4. 実行

```bash
python main.py
```

成功すると `output.mp3` が生成されます。

