from __future__ import annotations

from enum import StrEnum, auto
from typing import Any, Self

from src.domain.errors import MissingParameterError, RoleTypeError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class RoleType(StrEnum):
    ADMIN = auto()
    USER = auto()


class Role(ValueObject):
    def __init__(self: Self, role_type: str) -> None:
        self._role_type = RoleType(role_type)

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Role):
            return False
        return other.role_type == self._role_type

    @property
    def role_type(self: Self) -> RoleType:
        return self._role_type

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        role_type = kwargs.get("role_type")
        role_validation_result = cls.validate(role_type=role_type)
        if role_validation_result.is_failure:
            return role_validation_result
        return Result.ok(Role(role_type))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        role_type = kwargs.get("role_type")
        errors = []
        if role_type is None:
            errors.append(MissingParameterError("role_type"))
            return Result.fail(errors)
        if role_type not in [RoleType.ADMIN.value, RoleType.USER.value]:
            errors.append(RoleTypeError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
