"""
Custom crewAI tool: semantic search over the FAISS index built in Step 3.

Returns the top-k matching chunks with their similarity scores and a
"CONFIDENCE" verdict, so the agent (and later the crew) can decide whether
the knowledge base really answered the question.
"""

import json
import os
from pathlib import Path
from typing import Type

import faiss
import numpy as np
from crewai.tools import BaseTool
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

STORE_DIR = Path(os.getenv("VECTOR_STORE_DIR", "vector_store"))
EMBED_MODEL = "text-embedding-3-small"

# Similarity cut-off (cosine, 0..1). Below this the knowledge base is treated
# as NOT having the answer -> Agent 2 (web search) takes over.
MIN_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.40"))
TOP_K = int(os.getenv("TOP_K", "4"))


class VectorSearchInput(BaseModel):
    """Input schema for the vector search tool."""
    query: str = Field(..., description="The employee's question, or a focused search phrase.")


class CompanyPolicySearchTool(BaseTool):
    name: str = "company_policy_search"
    description: str = (
        "Searches NovaWave Technologies' internal documents (HR policy, leave policy, "
        "code of conduct, hybrid work, IT & security, employee FAQ). "
        "Returns the most relevant passages with similarity scores and a confidence verdict."
    )
    args_schema: Type[BaseModel] = VectorSearchInput

    def _run(self, query: str) -> str:
        index, chunks = _load_store()
        client = OpenAI()

        resp = client.embeddings.create(model=EMBED_MODEL, input=[query])
        q_vec = np.array([resp.data[0].embedding], dtype="float32")
        faiss.normalize_L2(q_vec)

        scores, ids = index.search(q_vec, TOP_K)
        best = float(scores[0][0])
        confidence = "HIGH" if best >= MIN_SCORE else "LOW"

        lines = [
            f"BEST_SCORE: {best:.3f} (threshold {MIN_SCORE})",
            f"CONFIDENCE: {confidence}",
        ]
        if confidence == "LOW":
            lines.append("NOTE: No passage is a strong match. The answer is probably NOT in the company documents.")
        lines.append("")

        for rank, (score, idx) in enumerate(zip(scores[0], ids[0]), start=1):
            if idx == -1:
                continue
            c = chunks[idx]
            lines.append(f"--- Result {rank} | score={score:.3f} | source={c['source']} > {c['section']}")
            lines.append(c["text"])
            lines.append("")

        return "\n".join(lines)


# Load once and cache (FAISS index + chunk texts)
_cache: dict = {}


def _load_store():
    if "index" not in _cache:
        index_path = STORE_DIR / "faiss.index"
        chunks_path = STORE_DIR / "chunks.json"
        if not index_path.exists():
            raise FileNotFoundError(f"{index_path} not found - run `python build_index.py` first.")
        _cache["index"] = faiss.read_index(str(index_path))
        _cache["chunks"] = json.loads(chunks_path.read_text(encoding="utf-8"))
    return _cache["index"], _cache["chunks"]
