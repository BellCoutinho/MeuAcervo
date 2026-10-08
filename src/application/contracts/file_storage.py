from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


class FileStorageService(ABC):

    @abstractmethod
    def save(self: Self, file_content: bytes, file_name: str, sub_dir: str) -> str:
        pass

    @abstractmethod
    def delete(self: Self, file_path: str) -> bool:
        pass

    @abstractmethod
    def get_path(self: Self, file_path: str) -> str:
        pass
