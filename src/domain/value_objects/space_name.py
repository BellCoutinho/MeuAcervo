from __future__ import annotations

from typing import Any, Self

from src.domain.errors import (
    MissingParameterError,
    TooLongSpaceNameError,
    TooShortSpaceNameError,
)
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class SpaceName(ValueObject):
    MINIMUM_LENGTH: int = 3
    MAXIMUM_LENGTH: int = 100

    def __init__(self: Self, name: str) -> None:
        self._name = name

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, SpaceName):
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
        return Result.ok(SpaceName(name))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        name = kwargs.get("name")
        errors = []
        if name is None:
            errors.append(MissingParameterError("name"))
            return Result.fail(errors)
        if len(name) < cls.MINIMUM_LENGTH:
            errors.append(TooShortSpaceNameError())
        if len(name) > cls.MAXIMUM_LENGTH:
            errors.append(TooLongSpaceNameError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
