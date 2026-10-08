from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import SpaceNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import SpaceRepository, UserRepository


class GetStorageInfoData(NamedTuple):
    user_id: str
    space_id: str


class GetSpaceStorageInfo(UseCase):
    def __init__(
        self: Self,
        space_repository: SpaceRepository,
        user_repository: UserRepository,
    ) -> None:
        self._space_repository = space_repository
        self._user_repository = user_repository

    def perform(
        self: Self,
        parameters: GetStorageInfoData,
    ) -> Result[dict, list[DomainError | SpaceNotExistsError]]:
        from uuid import UUID
        try:
            space_id = UUID(parameters.space_id)
        except ValueError:
            return Result.fail([SpaceNotExistsError("Invalid space ID")])

        space = self._space_repository.find_by_id(space_id)
        if space is None:
            return Result.fail([SpaceNotExistsError("Space not found")])

        users = self._user_repository.find_all_by_space(space_id)
        users_info = []
        total_used = 0
        for user in users:
            user_storage = user.storage_used
            total_used += user_storage
            users_info.append({
                "user_id": str(user.id),
                "name": user.name.full_name,
                "storage_used": user_storage,
            })

        return Result.ok({
            "space_id": str(space.id),
            "storage_quota": space.storage_quota,
            "total_used": total_used,
            "users": users_info,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: GetStorageInfoData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
