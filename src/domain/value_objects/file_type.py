from __future__ import annotations

from enum import StrEnum, auto
from typing import Any, Self

from src.domain.errors import InvalidFileTypeError, MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class FileType(StrEnum):
    NF = auto()
    PHOTO = auto()
    VIDEO = auto()
    CONTRACT = auto()
    OTHER = auto()


class FileTypeVO(ValueObject):
    def __init__(self: Self, file_type: str) -> None:
        self._file_type = FileType(file_type)

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, FileTypeVO):
            return False
        return other.file_type == self._file_type

    @property
    def file_type(self: Self) -> FileType:
        return self._file_type

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        file_type = kwargs.get("file_type")
        validation = cls.validate(file_type=file_type)
        if validation.is_failure:
            return validation
        return Result.ok(FileTypeVO(file_type))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        file_type = kwargs.get("file_type")
        errors = []
        if file_type is None:
            errors.append(MissingParameterError("file_type"))
            return Result.fail(errors)
        if file_type not in [e.value for e in FileType]:
            errors.append(InvalidFileTypeError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
