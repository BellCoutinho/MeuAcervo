from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.errors import DomainError

from src.domain.contracts import Entity
from src.domain.value_objects import (
    Address,
    Date,
    SpaceName,
    UniqueId,
    UtilityUnitNumber,
)
from src.shared import Result


class Space(Entity):
    def __init__(
        self: Self,
        name: SpaceName,
        address: Address,
        utility_unit_number: UtilityUnitNumber,
        id: UniqueId | None = None,
        storage_quota: int = 1073741824,
        created_at: Date | None = None,
    ) -> None:
        self._name = name
        self._address = address
        self._utility_unit_number = utility_unit_number
        self._unique_id = id or UniqueId()
        self._storage_quota = storage_quota
        self._created_at = created_at or Date()

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Space):
            return False
        return other.id == self._unique_id

    @property
    def id(self: Self) -> UUID:
        return self._unique_id.identifier

    @property
    def name(self: Self) -> SpaceName:
        return self._name

    @property
    def address(self: Self) -> Address:
        return self._address

    @property
    def utility_unit_number(self: Self) -> UtilityUnitNumber:
        return self._utility_unit_number

    @property
    def storage_quota(self: Self) -> int:
        return self._storage_quota

    @property
    def created_at(self: Self) -> Date:
        return self._created_at

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        name_result = SpaceName.create(name=kwargs.get("name"))
        address_result = Address.create(address=kwargs.get("address"))
        ucn_result = UtilityUnitNumber.create(number=kwargs.get("utility_unit_number"))
        id = kwargs.get("id")
        id_result = UniqueId.create(id=id) if id is not None else UniqueId.create()
        storage_quota = kwargs.get("storage_quota", 1073741824)

        validation_result = Result.combine(
            name_result, address_result, ucn_result, id_result
        )
        if validation_result.is_failure:
            return validation_result
        return Result.ok(Space(
            name=name_result.value,
            address=address_result.value,
            utility_unit_number=ucn_result.value,
            id=id_result.value,
            storage_quota=storage_quota,
        ))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        name_result = SpaceName.validate(name=kwargs.get("name"))
        address_result = Address.validate(address=kwargs.get("address"))
        ucn_result = UtilityUnitNumber.validate(number=kwargs.get("utility_unit_number"))
        return Result.combine(name_result, address_result, ucn_result)
