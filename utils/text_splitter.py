import re
from typing import List

def split_text(text: str, max_chars: int = 1500) -> List[str]:
    """
    長文を指定された文字数以下に分割する。
    句読点（。！？）や改行を優先して区切ることで、不自然な切れ目を防ぐ。
    
    Args:
        text: 分割対象のテキスト
        max_chars: 1チャンクあたりの最大文字数（Gemini TTSの制限や安全マージンを考慮）
    
    Returns:
        分割されたテキストのリスト
    """
    # 空白文字を除去しすぎないように注意しつつ、余計な空白は整理
    text = text.strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks = []
    current_chunk = ""

    # 優先度の高い区切り文字パターン
    # 1. 改行 + インデント等
    # 2. 句点（。）
    # 3. 読点（、）
    # それでも長すぎる場合は強制分割
    
    # 段落ごとにまず分ける
    paragraphs = re.split(r'(\n+)', text)
    
    for paragraph in paragraphs:
        # 改行文字そのものはそのまま追加候補へ
        if re.match(r'\n+', paragraph):
            if len(current_chunk) + len(paragraph) <= max_chars:
                current_chunk += paragraph
            else:
                # 改行だけでオーバーフローすることは稀だが、念のため
                chunks.append(current_chunk)
                current_chunk = paragraph
            continue

        # 段落が制限内なら追加
        if len(current_chunk) + len(paragraph) <= max_chars:
            current_chunk += paragraph
            continue
        
        # 段落が長すぎる場合、句点で分割
        sentences = re.split(r'([。！？])', paragraph)
        temp_sentence = ""
        
        for i in range(0, len(sentences), 2):
            # 文の内容
            part = sentences[i]
            # 区切り文字（もしあれば）
            delimiter = sentences[i+1] if i+1 < len(sentences) else ""
            
            full_sentence = part + delimiter
            
            if len(current_chunk) + len(temp_sentence) + len(full_sentence) <= max_chars:
                temp_sentence += full_sentence
            else:
                # 現在のチャンクに追加できるなら追加してフラッシュ
                if len(current_chunk) + len(temp_sentence) <= max_chars:
                    current_chunk += temp_sentence
                    chunks.append(current_chunk)
                    current_chunk = ""
                    temp_sentence = full_sentence
                else:
                    # temp_sentence自体が長すぎる場合（あまりないはずだが）
                    # 強制的にフラッシュ
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = ""
                    
                    if len(temp_sentence) > 0:
                         chunks.append(temp_sentence)
                         temp_sentence = ""
                    
                    # それでもfull_sentenceが入らない場合（非常に長い一文など）
                    # 読点「、」でさらに分割を試みるか、強制分割が必要
                    # ここでは簡易的に、入るだけ入れて次へ回す処理にする
                    if len(full_sentence) > max_chars:
                        # 非常に長い文は強制分割
                        while len(full_sentence) > max_chars:
                            chunks.append(full_sentence[:max_chars])
                            full_sentence = full_sentence[max_chars:]
                        current_chunk = full_sentence
                    else:
                        current_chunk = full_sentence

        # 残りの文を追加
        if temp_sentence:
            if len(current_chunk) + len(temp_sentence) <= max_chars:
                current_chunk += temp_sentence
            else:
                chunks.append(current_chunk)
                current_chunk = temp_sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

if __name__ == "__main__":
    # テスト用
    sample_text = "これはテストです。" * 100
    print(f"Original length: {len(sample_text)}")
    chunks = split_text(sample_text, max_chars=200)
    print(f"Chunks: {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"--- Chunk {i+1} ({len(c)} chars) ---")
        print(c[:30] + "...")
