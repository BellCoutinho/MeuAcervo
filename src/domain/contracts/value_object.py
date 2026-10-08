from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.shared.result import Result

T = TypeVar("T", bound="ValueObject")


class ValueObject(ABC):
    @abstractmethod
    def __eq__(self: T, other: T) -> bool:
        raise NotImplementedError("ValueObject: Equal method should be implemented")

    @abstractclassmethod
    def create(cls: type[T], **kwargs: dict[str, Any]) -> Result[T, list[DomainError]]:
        raise NotImplementedError("ValueObject: Create method should be implemented")

    @abstractclassmethod
    def validate(
        cls: type[T], **kwargs: dict[str, Any],
    ) -> Result[bool, list[DomainError]]:
        raise NotImplementedError("ValueObject: Validate method should be implemented")
