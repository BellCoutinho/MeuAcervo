from __future__ import annotations

from typing import Any, Self

from src.domain.errors import MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Brand(ValueObject):
    MINIMUM_LENGTH: int = 1
    MAXIMUM_LENGTH: int = 100

    def __init__(self: Self, brand: str) -> None:
        self._brand = brand

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Brand):
            return False
        return other.brand == self._brand

    @property
    def brand(self: Self) -> str:
        return self._brand

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        brand = kwargs.get("brand")
        validation = cls.validate(brand=brand)
        if validation.is_failure:
            return validation
        return Result.ok(Brand(brand))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        brand = kwargs.get("brand")
        errors = []
        if brand is None or len(str(brand).strip()) == 0:
            errors.append(MissingParameterError("brand"))
            return Result.fail(errors)
        if len(brand) < cls.MINIMUM_LENGTH or len(brand) > cls.MAXIMUM_LENGTH:
            errors.append(MissingParameterError("brand"))
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
