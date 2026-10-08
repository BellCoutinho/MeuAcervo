from __future__ import annotations

from src.application.contracts import ObjectStorageService
from src.infrastructure.storage import SqliteFsObjectStore

_object_storage_instance: SqliteFsObjectStore | None = None


def make_object_storage() -> ObjectStorageService:
    global _object_storage_instance
    if _object_storage_instance is None:
        _object_storage_instance = SqliteFsObjectStore()
    return _object_storage_instance
