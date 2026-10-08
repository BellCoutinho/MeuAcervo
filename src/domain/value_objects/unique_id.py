from __future__ import annotations

from typing import Any, Self
from uuid import UUID, uuid4

from src.domain.errors import InvalidUUIDUniqueIdError, MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result, is_uuid


class UniqueId(ValueObject):
    def __init__(self: Self, id: str | None = None) -> None:
        self._id = UUID(id, version=4) if id else uuid4()

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, UniqueId):
            return False
        return other.id == self._id

    def __repr__(self: Self) -> str:
        return f"UniqueId(id={self._id})"

    def __str__(self: Self) -> str:
        return str(self._id)

    @property
    def identifier(self: Self) -> UUID:
        return self._id

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        unique_id = kwargs.get("id")
        if unique_id is None:
            return Result.ok(UniqueId())
        id_validation_result = cls.validate(id=unique_id)
        if id_validation_result.is_failure:
            return id_validation_result
        return Result.ok(UniqueId(str(unique_id)))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        unique_id = kwargs.get("id")
        errors = []
        if unique_id is None:
            errors.append(MissingParameterError('id'))
            return Result.fail(errors)
        if not is_uuid(str(unique_id)):
            errors.append(InvalidUUIDUniqueIdError(unique_id))
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
