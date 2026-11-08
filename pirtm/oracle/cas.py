"""Content-Addressed Storage (CAS) with cryptographic provenance."""

from __future__ import annotations
import hashlib
import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


def compute_sha256(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class ProvenanceEntry:
    artifact_id: str
    sha256: str
    creator: str
    created_at_utc: str
    metadata: Dict[str, Any]
    parent_ids: list[str]


class ContentAddressedStore:
    """Immutable, append-only content-addressed store."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir
        self._memory_store: Dict[str, bytes] = {}
        self._provenance_store: Dict[str, ProvenanceEntry] = {}

        if self.storage_dir:
            os.makedirs(self.storage_dir, exist_ok=True)
            os.makedirs(os.path.join(self.storage_dir, "blobs"), exist_ok=True)
            os.makedirs(os.path.join(self.storage_dir, "provenance"), exist_ok=True)

    def put(
        self,
        content: bytes | str,
        creator: str,
        created_at_utc: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_ids: Optional[list[str]] = None,
    ) -> str:
        """Stores content immutably and returns its content hash (SHA-256)."""
        raw_bytes = content.encode("utf-8") if isinstance(content, str) else content
        sha = compute_sha256(raw_bytes)

        if sha in self._memory_store:
            # Immutability check: content must be identical
            existing = self._memory_store[sha]
            if existing != raw_bytes:
                raise ValueError(f"Hash collision or tampering detected for artifact {sha}")
            return sha

        self._memory_store[sha] = raw_bytes

        provenance = ProvenanceEntry(
            artifact_id=sha,
            sha256=sha,
            creator=creator,
            created_at_utc=created_at_utc,
            metadata=metadata or {},
            parent_ids=parent_ids or [],
        )
        self._provenance_store[sha] = provenance

        if self.storage_dir:
            blob_path = os.path.join(self.storage_dir, "blobs", sha)
            if not os.path.exists(blob_path):
                with open(blob_path, "wb") as f:
                    f.write(raw_bytes)
            prov_path = os.path.join(self.storage_dir, "provenance", f"{sha}.json")
            if not os.path.exists(prov_path):
                with open(prov_path, "w", encoding="utf-8") as f:
                    json.dump(asdict(provenance), f, indent=2)

        return sha

    def get(self, artifact_id: str) -> Optional[bytes]:
        """Resolves raw content by content hash."""
        if artifact_id in self._memory_store:
            return self._memory_store[artifact_id]

        if self.storage_dir:
            blob_path = os.path.join(self.storage_dir, "blobs", artifact_id)
            if os.path.exists(blob_path):
                with open(blob_path, "rb") as f:
                    data = f.read()
                self._memory_store[artifact_id] = data
                return data

        return None

    def get_provenance(self, artifact_id: str) -> Optional[ProvenanceEntry]:
        """Resolves provenance metadata by artifact hash."""
        if artifact_id in self._provenance_store:
            return self._provenance_store[artifact_id]

        if self.storage_dir:
            prov_path = os.path.join(self.storage_dir, "provenance", f"{artifact_id}.json")
            if os.path.exists(prov_path):
                with open(prov_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prov = ProvenanceEntry(**data)
                self._provenance_store[artifact_id] = prov
                return prov

        return None

    def verify(self, artifact_id: str) -> Dict[str, Any]:
        """Verifies integrity and provenance of an artifact."""
        content = self.get(artifact_id)
        if content is None:
            return {
                "artifact_id": artifact_id,
                "exists": False,
                "integrity_valid": False,
                "has_provenance": False,
                "error": "Artifact content not found",
            }

        actual_sha = compute_sha256(content)
        integrity_valid = actual_sha == artifact_id
        prov = self.get_provenance(artifact_id)

        return {
            "artifact_id": artifact_id,
            "exists": True,
            "integrity_valid": integrity_valid,
            "has_provenance": prov is not None,
            "creator": prov.creator if prov else None,
            "created_at_utc": prov.created_at_utc if prov else None,
            "parent_ids": prov.parent_ids if prov else [],
        }
