from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.errors import DomainError

from src.domain.contracts import Entity
from src.domain.value_objects import Name, Role, UniqueId
from src.shared import Result


class User(Entity):
    def __init__(
        self: Self,
        name: Name,
        id: UniqueId | None = None,
        role: Role | None = None,
        is_approved: bool = False,
        storage_used: int = 0,
        space_id: UUID | None = None,
    ) -> None:
        self._name = name
        self._unique_id = id or UniqueId()
        self._role = role or Role("user")
        self._is_approved = is_approved
        self._storage_used = storage_used
        self._space_id = space_id

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, User):
            return False
        return other.id == self._unique_id

    @property
    def id(self: Self) -> UUID:
        return self._unique_id.identifier

    @property
    def name(self: Self) -> Name:
        return self._name

    @property
    def role(self: Self) -> Role:
        return self._role

    @property
    def is_approved(self: Self) -> bool:
        return self._is_approved

    @property
    def storage_used(self: Self) -> int:
        return self._storage_used

    @property
    def space_id(self: Self) -> UUID | None:
        return self._space_id

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        name_result = Name.create(
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
        )
        id = kwargs.get("id")
        id_result = UniqueId.create(id=id) if id is not None else UniqueId.create()
        role = kwargs.get("role")
        role_result = (
            Role.create(role_type=role)
            if role is not None
            else Role.create(role_type="user")
        )

        validation_result = Result.combine(name_result, id_result, role_result)
        if validation_result.is_failure:
            return validation_result
        return Result.ok(User(
            name=name_result.value,
            id=id_result.value,
            role=role_result.value,
            is_approved=kwargs.get("is_approved", False),
            storage_used=kwargs.get("storage_used", 0),
            space_id=kwargs.get("space_id"),
        ))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        name_result = Name.validate(
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
        )
        return Result.combine(name_result)
