from __future__ import annotations

from datetime import date, datetime
from typing import Any, Self

from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class WarrantyDate(ValueObject):

    def __init__(self: Self, date_str: str | None = None) -> None:
        if date_str:
            self._date = datetime.fromisoformat(date_str).date()
        else:
            self._date = None

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, WarrantyDate):
            return False
        return other.value == self._date

    @property
    def value(self: Self) -> date | None:
        return self._date

    @property
    def is_active(self: Self) -> bool:
        if self._date is None:
            return False
        return self._date > date.today()

    @property
    def days_remaining(self: Self) -> int | None:
        if self._date is None:
            return None
        delta = self._date - date.today()
        return max(0, delta.days)

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        date_value = kwargs.get("date")
        if date_value is None:
            return Result.ok(WarrantyDate())
        if isinstance(date_value, str):
            try:
                datetime.fromisoformat(date_value)
            except ValueError:
                return Result.ok(WarrantyDate())
        return Result.ok(WarrantyDate(str(date_value) if date_value else None))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(value=True)
