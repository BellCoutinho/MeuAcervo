from __future__ import annotations

from datetime import date, datetime
from typing import Any, Self

from src.domain.errors import InvalidDateError, MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Date(ValueObject):
    def __init__(self: Self, date_str: str | None = None) -> None:
        if date_str:
            self._date = datetime.fromisoformat(date_str).date()
        else:
            self._date = date.today()

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Date):
            return False
        return other.value == self._date

    @property
    def value(self: Self) -> date:
        return self._date

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        date_value = kwargs.get("date")
        if date_value is None:
            return Result.ok(Date())
        date_validation_result = cls.validate(date=str(date_value))
        if date_validation_result.is_failure:
            return date_validation_result
        return Result.ok(Date(str(date_value)))

    @classmethod
    def validate(
        cls: type[Self],
        **kwargs: dict[str, Any],
    ) -> Result[bool, list[Exception]]:
        date_value = kwargs.get("date")
        errors = []
        if date_value is None:
            errors.append(MissingParameterError("date"))
            return Result.fail(errors)
        if not isinstance(date_value, str):
            errors.append(InvalidDateError())
            return Result.fail(errors)
        try:
            datetime.fromisoformat(date_value)
        except ValueError:
            errors.append(InvalidDateError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
