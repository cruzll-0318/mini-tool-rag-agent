def load_chunks(file_path):
    """读取知识文件，并按空行切分为片段。"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        return []

    parts = content.split("\n\n")
    chunks = []

    for index, text in enumerate(parts, start=1):
        text = text.strip()
        if text != "":
            chunks.append({
                "id": index,
                "text": text,
            })

    return chunks


def search_chunks(chunks, keyword):
    """使用简单关键词匹配查找资料片段。"""
    results = []
    keyword = keyword.lower()

    for chunk in chunks:
        if keyword in chunk["text"].lower():
            results.append(chunk)

    return results
