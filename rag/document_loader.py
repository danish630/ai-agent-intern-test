from pathlib import Path
import re


KNOWLEDGE_BASE_DIR = Path("knowledge-base")


def parse_frontmatter(content):
    match = re.match(
        r"^---\s*\n(.*?)\n---\s*\n(.*)$",
        content,
        re.DOTALL
    )

    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    body = match.group(2)

    metadata = {}

    for line in frontmatter_text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata, body


def chunk_document(body):
    sections = re.split(r"\n(?=## )", body)

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        lines = section.splitlines()

        heading = lines[0].replace("## ", "").strip()
        text = "\n".join(lines[1:]).strip()

        if text:
            chunks.append({
                "heading": heading,
                "text": text
            })

    return chunks


def load_documents():
    documents = []

    for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")

        metadata, body = parse_frontmatter(content)
        chunks = chunk_document(body)

        for chunk in chunks:
            documents.append({
                "filename": file_path.name,
                "metadata": metadata,
                "heading": chunk["heading"],
                "content": chunk["text"]
            })

    return documents


if __name__ == "__main__":
    documents = load_documents()

    print(f"Created {len(documents)} chunks")

    for document in documents[:10]:
        print(
            f"\n[{document['filename']}]"
            f"\nHeading: {document['heading']}"
            f"\nContent: {document['content'][:120]}..."
        )