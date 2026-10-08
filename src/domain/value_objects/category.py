from __future__ import annotations

from enum import StrEnum, auto
from typing import Any, Self

from src.domain.errors import InvalidProductCategoryError, MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class CategoryType(StrEnum):
    ELETRONICO = auto()
    ELETRODOMESTICO = auto()
    MOVEIS = auto()
    UTENSILIOS = auto()
    OUTROS = auto()


class Category(ValueObject):
    def __init__(self: Self, category: str) -> None:
        self._category = CategoryType(category)

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Category):
            return False
        return other.category == self._category

    @property
    def category(self: Self) -> CategoryType:
        return self._category

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        category = kwargs.get("category")
        validation = cls.validate(category=category)
        if validation.is_failure:
            return validation
        return Result.ok(Category(category))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        category = kwargs.get("category")
        errors = []
        if category is None:
            errors.append(MissingParameterError("category"))
            return Result.fail(errors)
        if category not in [e.value for e in CategoryType]:
            errors.append(InvalidProductCategoryError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
