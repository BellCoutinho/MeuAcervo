from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


class HashService(ABC):

    @abstractmethod
    def hash(self: Self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self: Self, password: str, digest: str) -> bool:
        pass
