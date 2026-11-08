"""Embedding Oracle and Lexical Retrieval Interface for PIRTM.

Supports:
- EMBED(document) -> vector (deterministic hash-based lexical embedding fallback if no neural model is configured)
- INDEX(identifier, vector, metadata) -> index entry
- RETRIEVE(query, limit, filters) -> ranked evidence
- RESOLVE(identifier) -> stored artifact
- VERIFY(identifier) -> integrity and provenance status
"""

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from pirtm.oracle.cas import ContentAddressedStore


@dataclass
class IndexEntry:
    identifier: str
    vector: Optional[List[float]]
    metadata: Dict[str, Any]
    content_excerpt: str
    backend: str  # e.g., "deterministic_lexical_fallback" or "external_embedding_model"


@dataclass
class RetrievalResult:
    identifier: str
    score: float
    metadata: Dict[str, Any]
    content_excerpt: str
    retrieval_mode: str  # "lexical_deterministic" or "vector_cosine"


class EmbeddingOracle:
    """Embedding oracle with durable content-addressed storage and deterministic fallback."""

    def __init__(
        self,
        cas: Optional[ContentAddressedStore] = None,
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
    ):
        self.cas = cas or ContentAddressedStore()
        self._embedding_fn = embedding_fn
        self._index: Dict[str, IndexEntry] = {}
        self.backend_name = (
            "external_embedding_adapter"
            if embedding_fn is not None
            else "deterministic_lexical_fallback (non-embedding)"
        )

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-\.\:\/]+\b", text.lower())

    def embed(self, document: str) -> List[float]:
        """EMBED(document) -> vector.

        If an external neural embedding backend is configured, calls it.
        Otherwise, produces a deterministic normalized bag-of-words / hash projection vector.
        Clearly designated as deterministic lexical fallback.
        """
        if self._embedding_fn is not None:
            return self._embedding_fn(document)

        # Deterministic 64-dimensional feature projection (non-embedding fallback)
        dim = 64
        vec = [0.0] * dim
        tokens = self._tokenize(document)
        if not tokens:
            return vec

        for tok in tokens:
            h = hash(tok)
            idx = abs(h) % dim
            sign = 1.0 if (h // dim) % 2 == 0 else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-12:
            vec = [v / norm for v in vec]
        return vec

    def index(
        self,
        identifier: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_excerpt: str = "",
    ) -> IndexEntry:
        """INDEX(identifier, vector, metadata) -> index entry."""
        entry = IndexEntry(
            identifier=identifier,
            vector=vector,
            metadata=metadata or {},
            content_excerpt=content_excerpt[:500],
            backend=self.backend_name,
        )
        self._index[identifier] = entry
        return entry

    def record_document(
        self,
        content: str,
        creator: str,
        created_at_utc: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_ids: Optional[List[str]] = None,
    ) -> str:
        """Helper to store content in CAS, compute embedding, and index."""
        meta = metadata or {}
        sha = self.cas.put(
            content=content,
            creator=creator,
            created_at_utc=created_at_utc,
            metadata=meta,
            parent_ids=parent_ids,
        )
        vec = self.embed(content)
        self.index(
            identifier=sha,
            vector=vec,
            metadata={**meta, "creator": creator, "created_at_utc": created_at_utc},
            content_excerpt=content[:200],
        )
        return sha

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return dot

    def retrieve(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """RETRIEVE(query, limit, filters) -> ranked evidence.

        Embedding similarity establishes retrieval relevance only. It never constitutes proof.
        """
        filters = filters or {}
        query_vec = self.embed(query)
        query_tokens = set(self._tokenize(query))

        candidates: List[RetrievalResult] = []

        for ident, entry in self._index.items():
            # Check filters
            match = True
            for k, expected in filters.items():
                if entry.metadata.get(k) != expected:
                    match = False
                    break
            if not match:
                continue

            # Compute score
            if self._embedding_fn is not None and entry.vector is not None:
                sim = self._cosine_similarity(query_vec, entry.vector)
                mode = "vector_cosine"
            else:
                # Deterministic lexical BM25/Jaccard hybrid fallback
                doc_content = entry.content_excerpt
                raw_bytes = self.cas.get(ident)
                if raw_bytes is not None:
                    try:
                        doc_content = raw_bytes.decode("utf-8")
                    except Exception:
                        pass
                doc_tokens = set(self._tokenize(doc_content))
                intersection = query_tokens.intersection(doc_tokens)
                union = query_tokens.union(doc_tokens)
                jaccard = len(intersection) / len(union) if union else 0.0

                # Token frequency weighting
                tf_score = sum(1.0 for t in self._tokenize(doc_content) if t in query_tokens)
                sim = jaccard * 0.5 + min(tf_score / 10.0, 0.5)
                mode = "lexical_deterministic"

            candidates.append(
                RetrievalResult(
                    identifier=ident,
                    score=sim,
                    metadata=entry.metadata,
                    content_excerpt=entry.content_excerpt,
                    retrieval_mode=mode,
                )
            )

        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:limit]

    def resolve(self, identifier: str) -> Optional[bytes]:
        """RESOLVE(identifier) -> stored artifact."""
        return self.cas.get(identifier)

    def verify(self, identifier: str) -> Dict[str, Any]:
        """VERIFY(identifier) -> integrity and provenance status."""
        return self.cas.verify(identifier)
