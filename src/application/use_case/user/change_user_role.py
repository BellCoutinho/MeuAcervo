from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import UnauthorizedError, UserNotExistError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class ChangeUserRoleData(NamedTuple):
    admin_id: str
    user_id: str
    new_role: str


class ChangeUserRole(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    def perform(
        self: Self,
        parameters: ChangeUserRoleData,
    ) -> Result[bool, list[DomainError | UserNotExistError | UnauthorizedError]]:
        from uuid import UUID
        try:
            user_id = UUID(parameters.user_id)
        except ValueError:
            return Result.fail([UserNotExistError("Invalid user ID")])

        user = self._user_repository.find_by_id(user_id)
        if user is None:
            return Result.fail([UserNotExistError("User not found")])

        from src.domain.value_objects import Role
        role_result = Role.create(role_type=parameters.new_role)
        if role_result.is_failure:
            return role_result

        user._role = role_result.value
        self._user_repository.update(user)

        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: ChangeUserRoleData,
    ) -> Result[bool, list[DomainError]]:
        from src.domain.value_objects import Role
        return Role.validate(role_type=parameters.new_role)
