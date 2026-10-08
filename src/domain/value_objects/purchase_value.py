from __future__ import annotations

from typing import Any, Self

from src.domain.errors import InvalidPurchaseValueError, MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class PurchaseValue(ValueObject):

    def __init__(self: Self, value: float) -> None:
        self._value = value

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, PurchaseValue):
            return False
        return other.value == self._value

    @property
    def value(self: Self) -> float:
        return self._value

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        value = kwargs.get("value")
        validation = cls.validate(value=value)
        if validation.is_failure:
            return validation
        return Result.ok(PurchaseValue(value))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        value = kwargs.get("value")
        errors = []
        if value is None:
            errors.append(MissingParameterError("value"))
            return Result.fail(errors)
        if value <= 0:
            errors.append(InvalidPurchaseValueError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
