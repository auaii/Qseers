"""Destiny Analyze Agent Tools — RAG search over the Wuxing face-reading knowledge base."""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
_COLLECTION = os.getenv("CHROMA_COLLECTION", "docs")
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Initialize at import time (main thread) — ChromaDB rust backend fails when
# first initialized inside a thread executor (langgraph tool node).
_embeddings = HuggingFaceEmbeddings(model_name=_MODEL_NAME)
_db = Chroma(
    collection_name=_COLLECTION,
    embedding_function=_embeddings,
    persist_directory=_DB_PATH,
)


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Record a strategic reflection before or after each analysis step.

    Use this to reason about which face features to look up next, assess
    whether enough knowledge has been retrieved, and plan the final report.

    Args:
        reflection: Detailed thoughts on current findings, gaps, and next steps.

    Returns:
        Confirmation that the reflection was recorded.
    """
    return f"Reflection recorded: {reflection}"


@tool(parse_docstring=True)
def RAG_Search(query: str, top_k: int = 3) -> str:
    """Search the Wuxing (五行相面) knowledge base for relevant face-reading information.

    Use this for every face feature before writing analysis. Query in Thai or Chinese
    for best results (e.g. "หน้าผากกว้าง โหง่วเฮ้ง", "จมูกใหญ่ ดวงการเงิน").

    Args:
        query: The search query describing the face feature or topic to look up.
        top_k: Number of knowledge chunks to return (default 3).

    Returns:
        Relevant knowledge chunks with source references.
    """
    results = _db.similarity_search_with_score(query, k=top_k)

    if not results:
        return "ไม่พบข้อมูลที่เกี่ยวข้องในฐานความรู้"

    output_parts = []
    for rank, (doc, dist) in enumerate(results, 1):
        source = Path(doc.metadata.get("source", "unknown")).name
        page = doc.metadata.get("page", "?")
        chunk_id = f"{source}:p{page}"
        output_parts.append(
            f"[chunk-{rank}] [{chunk_id}] dist={dist:.2f}\n{doc.page_content.strip()}"
        )

    return "\n\n---\n\n".join(output_parts)