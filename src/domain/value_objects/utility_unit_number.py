from __future__ import annotations

from typing import Any, Self

from src.domain.errors import MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class UtilityUnitNumber(ValueObject):

    def __init__(self: Self, number: str) -> None:
        self._number = number

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, UtilityUnitNumber):
            return False
        return other.number == self._number

    @property
    def number(self: Self) -> str:
        return self._number

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        number = kwargs.get("number")
        validation = cls.validate(number=number)
        if validation.is_failure:
            return validation
        return Result.ok(UtilityUnitNumber(number))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        number = kwargs.get("number")
        errors = []
        if number is None or len(str(number).strip()) == 0:
            errors.append(MissingParameterError("number"))
            return Result.fail(errors)
        return Result.ok(value=True)
