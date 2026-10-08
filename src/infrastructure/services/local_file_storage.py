import os
from typing import Self
from uuid import uuid4

from src.application.contracts import FileStorageService


class LocalFileStorageService(FileStorageService):
    def __init__(self: Self) -> None:
        self._base_dir = os.environ.get('UPLOAD_DIR', './uploads')
        os.makedirs(self._base_dir, exist_ok=True)

    def save(self: Self, file_content: bytes, file_name: str, sub_dir: str) -> str:
        dir_path = os.path.join(self._base_dir, sub_dir)
        os.makedirs(dir_path, exist_ok=True)

        ext = os.path.splitext(file_name)[1]
        unique_name = f"{uuid4().hex}{ext}"
        file_path = os.path.join(dir_path, unique_name)

        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_path

    def delete(self: Self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except OSError:
            return False

    def get_path(self: Self, file_path: str) -> str:
        return file_path
