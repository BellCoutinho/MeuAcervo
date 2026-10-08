from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from src.shared.result import Result


class TokenManager(ABC):

    @abstractmethod
    def create(self: Self, payload: dict) -> str:
        pass

    @abstractmethod
    def verify(self: Self, token: str) -> Result[dict, Exception]:
        pass
