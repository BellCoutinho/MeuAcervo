from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.entities import Space


class SpaceRepository(ABC):

    @abstractmethod
    def add(self: Self, space: Space) -> None:
        ...

    @abstractmethod
    def find_by_id(self: Self, id: UUID) -> Space | None:
        ...

    @abstractmethod
    def find_by_user_id(self: Self, user_id: UUID) -> Space | None:
        ...

    @abstractmethod
    def update(self: Self, space: Space) -> None:
        ...
