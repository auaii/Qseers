"""
Interactive query tool for ChromaDB vector store.

Usage:
    uv run query.py                          # interactive REPL
    uv run query.py "คำถาม"                 # single query
    uv run query.py --top-k 5 "คำถาม"
"""

import argparse
import io
import sys
import textwrap
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

SEPARATOR = "─" * 72
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_db(db_path: str, collection: str, model_name: str) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return Chroma(
        collection_name=collection,
        embedding_function=embeddings,
        persist_directory=db_path,
    )


def search(db: Chroma, query: str, top_k: int) -> None:
    # Returns (doc, L2_distance) — lower = more similar
    results = db.similarity_search_with_score(query, k=top_k)

    if not results:
        print("  (ไม่พบผลลัพธ์)")
        return

    dists = [d for _, d in results]
    d_min, d_max = min(dists), max(dists)
    span = (d_max - d_min) or 1.0  # avoid div-by-zero when all equal

    for rank, (doc, dist) in enumerate(results, 1):
        source = Path(doc.metadata.get("source", "unknown")).name
        page   = doc.metadata.get("page", "?")
        # Relative rank score within this result set: best chunk = 1.0
        rel = 1.0 - (dist - d_min) / span
        bar = "█" * int(rel * 10) + "░" * (10 - int(rel * 10))
        print(f"\n  #{rank}  dist={dist:.2f}  [{bar}] {rel:.0%}  [{source}  หน้า {page}]")
        print(SEPARATOR)
        wrapped = textwrap.fill(doc.page_content.strip(), width=70,
                                initial_indent="  ", subsequent_indent="  ")
        print(wrapped)

    print(f"\n  (dist ต่ำ = ใกล้เคียงกว่า | best={d_min:.2f}  worst={d_max:.2f})\n")


def run_repl(db: Chroma, top_k: int) -> None:
    print("Vector DB Query — พิมพ์คำถาม หรือ 'q' เพื่อออก\n")
    while True:
        try:
            query = input("? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query.lower() in {"q", "quit", "exit"}:
            break
        search(db, query, top_k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query ChromaDB vector store")
    parser.add_argument("query", nargs="?", help="คำถาม (ถ้าไม่ใส่จะเปิด REPL)")
    parser.add_argument("--db-path", default="./chroma_db")
    parser.add_argument("--collection", default="docs")
    parser.add_argument("--top-k", type=int, default=3, help="จำนวน chunks ที่ดึงกลับมา")
    parser.add_argument("--model", default=MODEL_NAME)
    args = parser.parse_args()

    print(f"[+] Loading DB from: {args.db_path}  collection={args.collection}")
    db = load_db(args.db_path, args.collection, args.model)
    total = db._collection.count()  # type: ignore[attr-defined]
    print(f"[+] {total} vectors loaded\n")

    if args.query:
        search(db, args.query, args.top_k)
    else:
        run_repl(db, args.top_k)
