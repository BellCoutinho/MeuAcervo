from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod
from typing import Self, TypeVar

from src.shared.result import Result

Incoming = TypeVar("Incoming")
Outgoing = TypeVar("Outgoing")


class UseCase(ABC):

    @abstractmethod
    def perform(self: Self, parameters: Incoming) -> Outgoing:
        pass

    @abstractclassmethod
    def validate_parameters(cls: type[Self], parameters: Incoming) -> Result[bool, list[Exception]]:
        pass
