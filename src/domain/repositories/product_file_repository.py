from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.entities import ProductFile


class ProductFileRepository(ABC):

    @abstractmethod
    def add(self: Self, file: ProductFile) -> None:
        ...

    @abstractmethod
    def find_by_id(self: Self, id: UUID) -> ProductFile | None:
        ...

    @abstractmethod
    def find_by_product_id(self: Self, product_id: UUID) -> list[ProductFile]:
        ...

    @abstractmethod
    def find_all_by_user(self: Self, user_id: UUID) -> list[ProductFile]:
        ...

    @abstractmethod
    def sum_size_by_user(self: Self, user_id: UUID) -> int:
        ...

    @abstractmethod
    def remove_by_id(self: Self, id: UUID) -> None:
        ...
