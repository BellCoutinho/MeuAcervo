from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import SpaceNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class GetSpaceUsersData(NamedTuple):
    user_id: str
    space_id: str


class GetSpaceUsers(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    def perform(
        self: Self,
        parameters: GetSpaceUsersData,
    ) -> Result[list[dict], list[DomainError | SpaceNotExistsError]]:
        from uuid import UUID
        try:
            space_id = UUID(parameters.space_id)
        except ValueError:
            return Result.fail([SpaceNotExistsError("Invalid space ID")])

        users = self._user_repository.find_all_by_space(space_id)
        users_list = []
        for user in users:
            users_list.append({
                "user_id": str(user.id),
                "name": user.name.full_name,
                "role": user.role.role_type.value,
                "is_approved": user.is_approved,
                "storage_used": user.storage_used,
            })

        return Result.ok(users_list)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: GetSpaceUsersData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
