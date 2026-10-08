from __future__ import annotations

from typing import Any, Self

from src.domain.errors import InvalidFileSizeError, MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class FileSize(ValueObject):

    def __init__(self: Self, size: int) -> None:
        self._size = size

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, FileSize):
            return False
        return other.size == self._size

    @property
    def size(self: Self) -> int:
        return self._size

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        size = kwargs.get("size")
        validation = cls.validate(size=size)
        if validation.is_failure:
            return validation
        return Result.ok(FileSize(size))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        size = kwargs.get("size")
        errors = []
        if size is None:
            errors.append(MissingParameterError("size"))
            return Result.fail(errors)
        if size <= 0:
            errors.append(InvalidFileSizeError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
