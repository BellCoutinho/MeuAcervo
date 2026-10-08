from __future__ import annotations

from typing import Any, Self

from src.domain.errors import MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class ProductName(ValueObject):
    MINIMUM_LENGTH: int = 2
    MAXIMUM_LENGTH: int = 150

    def __init__(self: Self, name: str) -> None:
        self._name = name

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, ProductName):
            return False
        return other.name == self._name

    @property
    def name(self: Self) -> str:
        return self._name

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        name = kwargs.get("name")
        validation = cls.validate(name=name)
        if validation.is_failure:
            return validation
        return Result.ok(ProductName(name))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        name = kwargs.get("name")
        errors = []
        if name is None or len(str(name).strip()) == 0:
            errors.append(MissingParameterError("name"))
            return Result.fail(errors)
        if len(name) < cls.MINIMUM_LENGTH or len(name) > cls.MAXIMUM_LENGTH:
            errors.append(MissingParameterError("name"))
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
