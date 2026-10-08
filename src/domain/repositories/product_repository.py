from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.entities import Product


class ProductRepository(ABC):

    @abstractmethod
    def add(self: Self, product: Product) -> None:
        ...

    @abstractmethod
    def find_by_id(self: Self, id: UUID) -> Product | None:
        ...

    @abstractmethod
    def find_by_space_id(self: Self, space_id: UUID) -> list[Product]:
        ...

    @abstractmethod
    def search(
        self: Self,
        space_id: UUID,
        term: str | None = None,
        category: str | None = None,
        warranty_status: str | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        ...

    @abstractmethod
    def update(self: Self, product: Product) -> None:
        ...

    @abstractmethod
    def update_status(self: Self, id: UUID, status: str, reason: str | None) -> None:
        ...

    @abstractmethod
    def remove_by_id(self: Self, id: UUID) -> None:
        ...
