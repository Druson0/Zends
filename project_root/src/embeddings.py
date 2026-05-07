from dotenv import load_dotenv
load_dotenv()  # loads variables from .env into os.environ

# src/embeddings.py
"""Embedding utilities for the RAG system.

This module provides a thin wrapper around OpenAI's embedding API (or any
compatible provider) to convert text into high‑dimensional vectors.
"""
import os
from typing import List

import numpy as np

# Try to import openai, fall back to a dummy implementation for offline use.
try:
    import groq
    GROQ_AVAILABLE = True
except Exception:  # pragma: no cover
    GROQ_AVAILABLE = False

# Default model – can be overridden via env var.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

def _embed_groq(texts: List[str]) -> List[List[float]]:
    """Call Groq's embedding endpoint.

    Parameters
    ----------
    texts: List[str]
        List of strings to embed.

    Returns
    -------
    List[List[float]]
        List of embedding vectors.
    """
    if not GROQ_AVAILABLE:
        raise RuntimeError("Groq package not installed.")
    response = groq.Embedding.create(model=EMBEDDING_MODEL, input=texts)
    return [emb['embedding'] for emb in response['data']]

def embed_texts(texts: List[str]) -> np.ndarray:
    """Return a NumPy array of shape (n, d) containing embeddings.

    For the purpose of this demo, if the Groq client is unavailable we fall
    back to a deterministic pseudo‑embedding based on SHA‑1 hashes – this keeps the
    code runnable in offline environments or CI pipelines.
    """
    if GROQ_AVAILABLE:
        vectors = _embed_groq(texts)
        return np.array(vectors, dtype=np.float32)
    # Simple deterministic fallback – hash each string and map to a fixed‑size vector.
    import hashlib
    dim = 1536  # match ada‑002 dimension
    vectors = []
    for txt in texts:
        h = hashlib.sha256(txt.encode()).digest()
        # Expand/truncate the hash to the desired dimension.
        arr = np.frombuffer(h * (dim // len(h) + 1), dtype=np.uint8)[:dim].astype(np.float32)
        vectors.append(arr)
    return np.stack(vectors)
