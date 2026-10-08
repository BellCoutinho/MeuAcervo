from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.shared.result import Result


class Entity(ABC):

    @abstractproperty
    def id(self: Self) -> UUID:
        raise NotImplementedError("Entity: Id property should be implemented")

    @abstractmethod
    def __eq__(self: Self, other: Self) -> bool:
        raise NotImplementedError("Entity: Equal method should be implemented")

    @abstractclassmethod
    def create(cls: type[Self], **kwargs: dict[str, Any]) -> Result[Self, list[Exception]]:
        raise NotImplementedError("Entity: Create method should be implemented")

    @abstractclassmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[Exception]]:
       raise NotImplementedError("Entity: Validate method should be implemented")
