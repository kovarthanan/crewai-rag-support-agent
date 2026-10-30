"""
Step 3 - Build the FAISS vector index from the company documents.

What it does:
  1. Reads every .md file in data/company_docs/
  2. Splits each file into chunks by markdown section (## / ### headings);
     long sections are split further with overlap
  3. Embeds every chunk with OpenAI (text-embedding-3-small)
  4. Saves:
       vector_store/faiss.index   -> the vectors (cosine similarity)
       vector_store/chunks.json   -> chunk text + metadata (source file, section)

Run:
  python build_index.py              # build the index
  python build_index.py --dry-run    # only show the chunks, no API calls
  python build_index.py --test "How many sick leaves do I get?"
"""

import argparse
import json
import os
import re
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DOCS_DIR = Path("data/company_docs")
STORE_DIR = Path("vector_store")
INDEX_PATH = STORE_DIR / "faiss.index"
CHUNKS_PATH = STORE_DIR / "chunks.json"

EMBED_MODEL = "text-embedding-3-small"
MAX_CHARS = 1200      # max characters per chunk
OVERLAP_CHARS = 200   # overlap when a long section is split


# ---------------------------------------------------------------- chunking
def split_long_text(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split text on paragraph/line boundaries, keeping chunks <= max_chars."""
    if len(text) <= max_chars:
        return [text]

    lines = text.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = current[-overlap:] + "\n" + line  # carry overlap forward
        else:
            current += "\n" + line
    if current.strip():
        chunks.append(current.strip())
    return chunks


def chunk_markdown(path: Path) -> list[dict]:
    """Split one markdown file into section-based chunks with metadata."""
    text = path.read_text(encoding="utf-8")

    # Document title = first "# " heading
    title_match = re.search(r"^# (.+)$", text, flags=re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else path.stem

    # Split before every ## or ### heading
    sections = re.split(r"(?=^#{2,3} )", text, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        heading_match = re.match(r"^#{1,3} (.+)$", section, flags=re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else doc_title

        for part in split_long_text(section, MAX_CHARS, OVERLAP_CHARS):
            # Prefix the doc title so every chunk carries its context
            chunks.append({
                "source": path.name,
                "doc_title": doc_title,
                "section": heading,
                "text": f"[{doc_title}]\n{part}",
            })
    return chunks


def load_all_chunks() -> list[dict]:
    files = sorted(DOCS_DIR.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No .md files found in {DOCS_DIR.resolve()}")

    all_chunks = []
    for f in files:
        file_chunks = chunk_markdown(f)
        print(f"  {f.name:<45} -> {len(file_chunks)} chunks")
        all_chunks.extend(file_chunks)

    for i, c in enumerate(all_chunks):
        c["id"] = i
    return all_chunks


# ---------------------------------------------------------------- embeddings
def embed_texts(client: OpenAI, texts: list[str], batch_size: int = 100) -> np.ndarray:
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        vectors.extend([d.embedding for d in resp.data])
    arr = np.array(vectors, dtype="float32")
    faiss.normalize_L2(arr)  # normalise -> inner product == cosine similarity
    return arr


# ---------------------------------------------------------------- build / test
def build_index():
    print(f"Reading documents from {DOCS_DIR}/ ...")
    chunks = load_all_chunks()
    print(f"Total chunks: {len(chunks)}")

    client = OpenAI()  # uses OPENAI_API_KEY from .env
    print(f"Embedding with {EMBED_MODEL} ...")
    vectors = embed_texts(client, [c["text"] for c in chunks])

    index = faiss.IndexFlatIP(vectors.shape[1])  # exact cosine search
    index.add(vectors)

    STORE_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    CHUNKS_PATH.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSaved {index.ntotal} vectors (dim={vectors.shape[1]})")
    print(f"  -> {INDEX_PATH}")
    print(f"  -> {CHUNKS_PATH}")


def test_search(query: str, top_k: int = 3):
    index = faiss.read_index(str(INDEX_PATH))
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))

    client = OpenAI()
    q_vec = embed_texts(client, [query])
    scores, ids = index.search(q_vec, top_k)

    print(f"\nQuery: {query}\n")
    for rank, (score, idx) in enumerate(zip(scores[0], ids[0]), start=1):
        c = chunks[idx]
        print(f"#{rank}  score={score:.3f}  {c['source']}  >  {c['section']}")
        print("    " + c["text"][:250].replace("\n", "\n    ") + " ...\n")


def dry_run():
    chunks = load_all_chunks()
    print(f"\nTotal chunks: {len(chunks)}\n")
    for c in chunks[:5]:
        print(f"--- #{c['id']}  {c['source']}  >  {c['section']}  ({len(c['text'])} chars)")
        print(c["text"][:200], "...\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="show chunks only, no API calls")
    parser.add_argument("--test", type=str, help="run a test search on the saved index")
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    elif args.test:
        test_search(args.test)
    else:
        if not os.getenv("OPENAI_API_KEY"):
            raise SystemExit("OPENAI_API_KEY missing - add it to your .env file")
        build_index()
