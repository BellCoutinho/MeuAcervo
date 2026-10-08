from __future__ import annotations

from typing import Any, Self

from src.domain.errors import MissingParameterError, TooLongNameError, TooShortNameError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Name(ValueObject):
    MINIMUM_NAME_LENGTH: int = 3
    MAXIMUM_NAME_LENGTH: int = 100

    def __init__(self: Self, first_name: str, last_name: str) -> None:
        self._first_name = first_name
        self._last_name = last_name

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Name):
            return False
        return other.first_name == self._first_name and other.last_name == self._last_name

    @property
    def full_name(self: Self) -> str:
        return self._first_name + ' ' + self._last_name

    @property
    def first_name(self: Self) -> str:
        return self._first_name

    @property
    def last_name(self: Self) -> str:
        return self._last_name

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        name_validation_result = Name.validate(first_name=first_name, last_name=last_name)
        if name_validation_result.is_failure:
            return name_validation_result
        return Result.ok(Name(first_name, last_name))

    @classmethod
    def validate(
        cls: type[Name],
        **kwargs: dict[str, Any],
    ) -> Result[bool, list[Exception]]:
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        errors = []
        if first_name is None:
            errors.append(MissingParameterError('first_name'))
        if last_name is None:
            errors.append(MissingParameterError('last_name'))
        if len(errors) > 0:
            return Result.fail(errors)
        full_name = first_name + ' ' + last_name
        if len(full_name) < Name.MINIMUM_NAME_LENGTH:
            errors.append(TooShortNameError())
        if len(full_name) > Name.MAXIMUM_NAME_LENGTH:
            errors.append(TooLongNameError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
