"""Evidence storage behind an interface (backend-spec 7, constitution ARC-7).

`FilesystemEvidenceStore` keeps documents under a directory, addressed by SHA-256, and re-checks the
hash on every read, so tampering or corruption is detected. The S3-compatible object store chosen
under T-009 will implement the same two methods.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Protocol

from app.domain.scanning import Evidence, RawDocument


class EvidenceStore(Protocol):
    def put(
        self,
        doc: RawDocument,
        *,
        source_type: str,
        collector: str,
        collector_version: str,
        collected_at: datetime,
    ) -> Evidence: ...
    def get(self, sha256: str) -> bytes: ...


class IntegrityError(Exception):
    """Stored evidence no longer matches its recorded hash."""


class FilesystemEvidenceStore:
    def __init__(self, root: Path) -> None:
        self._root = root

    def _path(self, sha256: str) -> Path:
        if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
            raise ValueError("invalid evidence hash")
        return self._root / sha256[:2] / sha256

    def put(
        self,
        doc: RawDocument,
        *,
        source_type: str,
        collector: str,
        collector_version: str,
        collected_at: datetime,
    ) -> Evidence:
        digest = hashlib.sha256(doc.content).hexdigest()
        path = self._path(digest)
        if not path.exists():  # content-addressed: identical evidence is stored once
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(doc.content)
            tmp.replace(path)
        return Evidence(
            sha256=digest,
            source_type=source_type,
            source_ref=doc.source_ref,
            collected_at=collected_at,
            collector=collector,
            collector_version=collector_version,
            size=len(doc.content),
        )

    def get(self, sha256: str) -> bytes:
        content = self._path(sha256).read_bytes()
        if hashlib.sha256(content).hexdigest() != sha256:
            raise IntegrityError(f"evidence {sha256} does not match its hash")
        return content
