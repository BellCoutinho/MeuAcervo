from __future__ import annotations

from typing import Any, Self

from src.domain.errors import MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Location(ValueObject):
    MINIMUM_LENGTH: int = 2
    MAXIMUM_LENGTH: int = 100

    def __init__(self: Self, location: str) -> None:
        self._location = location

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Location):
            return False
        return other.location == self._location

    @property
    def location(self: Self) -> str:
        return self._location

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        location = kwargs.get("location")
        validation = cls.validate(location=location)
        if validation.is_failure:
            return validation
        return Result.ok(Location(location))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        location = kwargs.get("location")
        errors = []
        if location is None or len(str(location).strip()) == 0:
            errors.append(MissingParameterError("location"))
            return Result.fail(errors)
        if len(location) < cls.MINIMUM_LENGTH or len(location) > cls.MAXIMUM_LENGTH:
            errors.append(MissingParameterError("location"))
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
