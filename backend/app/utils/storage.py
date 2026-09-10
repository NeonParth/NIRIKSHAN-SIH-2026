from __future__ import annotations

"""Abstract evidence storage. Phase 1 uses URI strings only (local files or URLs)."""

from pathlib import Path
from typing import Protocol


class StorageBackend(Protocol):
    def exists(self, uri: str) -> bool: ...


class LocalUriStorage:
    def exists(self, uri: str) -> bool:
        if uri.startswith("http://") or uri.startswith("https://"):
            return True
        path = Path(uri)
        return path.exists()
