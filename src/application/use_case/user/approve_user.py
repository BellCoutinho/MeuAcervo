from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import UnauthorizedError, UserNotExistError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class ApproveUserData(NamedTuple):
    admin_id: str
    user_id: str


class ApproveUser(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    def perform(
        self: Self,
        parameters: ApproveUserData,
    ) -> Result[bool, list[DomainError | UserNotExistError | UnauthorizedError]]:
        from uuid import UUID
        try:
            user_id = UUID(parameters.user_id)
        except ValueError:
            return Result.fail([UserNotExistError("Invalid user ID")])

        user = self._user_repository.find_by_id(user_id)
        if user is None:
            return Result.fail([UserNotExistError("User not found")])

        user._is_approved = True
        self._user_repository.update(user)

        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: ApproveUserData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
