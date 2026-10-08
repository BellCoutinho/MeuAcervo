from __future__ import annotations

import os

from src.application.contracts import FileStorageService
from src.infrastructure.services.local_file_storage import LocalFileStorageService
from src.infrastructure.storage import SqliteFsObjectStore


def make_file_storage() -> FileStorageService:
    storage_type = os.environ.get("STORAGE_TYPE", "sqlite_fs").lower()
    if storage_type == "local":
        return LocalFileStorageService()
    return SqliteFsObjectStore()
