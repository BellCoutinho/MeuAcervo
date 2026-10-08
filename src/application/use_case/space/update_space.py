from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import SpaceNotExistsError, UnauthorizedError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import SpaceRepository


class UpdateSpaceData(NamedTuple):
    user_id: str
    space_id: str
    name: str | None = None
    address: str | None = None
    utility_unit_number: str | None = None
    storage_quota: int | None = None


class UpdateSpace(UseCase):
    def __init__(
        self: Self,
        space_repository: SpaceRepository,
    ) -> None:
        self._space_repository = space_repository

    def perform(
        self: Self,
        parameters: UpdateSpaceData,
    ) -> Result[bool, list[DomainError | SpaceNotExistsError | UnauthorizedError]]:
        from uuid import UUID
        try:
            space_id = UUID(parameters.space_id)
        except ValueError:
            return Result.fail([SpaceNotExistsError("Invalid space ID")])

        space = self._space_repository.find_by_id(space_id)
        if space is None:
            return Result.fail([SpaceNotExistsError("Space not found")])

        if parameters.name:
            from src.domain.value_objects import SpaceName
            name_result = SpaceName.create(name=parameters.name)
            if name_result.is_failure:
                return name_result
            space._name = name_result.value

        if parameters.address:
            from src.domain.value_objects import Address
            addr_result = Address.create(address=parameters.address)
            if addr_result.is_failure:
                return addr_result
            space._address = addr_result.value

        if parameters.utility_unit_number:
            from src.domain.value_objects import UtilityUnitNumber
            ucn_result = UtilityUnitNumber.create(number=parameters.utility_unit_number)
            if ucn_result.is_failure:
                return ucn_result
            space._utility_unit_number = ucn_result.value

        if parameters.storage_quota is not None:
            space._storage_quota = parameters.storage_quota

        self._space_repository.update(space)
        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: UpdateSpaceData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
