from __future__ import annotations

from typing import Any, Self

from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class SerialNumber(ValueObject):

    def __init__(self: Self, serial_number: str | None = None) -> None:
        self._serial_number = serial_number

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, SerialNumber):
            return False
        return other.serial_number == self._serial_number

    @property
    def serial_number(self: Self) -> str | None:
        return self._serial_number

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        serial_number = kwargs.get("serial_number")
        if serial_number is None or str(serial_number).strip() == "":
            return Result.ok(SerialNumber())
        return Result.ok(SerialNumber(str(serial_number).strip()))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(value=True)
