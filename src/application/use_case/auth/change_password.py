from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import UserNotExistError, WrongPasswordError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import HashService
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class ChangePasswordData(NamedTuple):
    user_id: str
    current_password: str
    new_password: str


class ChangePassword(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
        hash_service: HashService,
    ) -> None:
        self._user_repository = user_repository
        self._hash_service = hash_service

    def perform(
        self: Self,
        parameters: ChangePasswordData,
    ) -> Result[bool, list[DomainError | UserNotExistError | WrongPasswordError]]:
        from uuid import UUID
        try:
            user_id = UUID(parameters.user_id)
        except ValueError:
            return Result.fail([UserNotExistError("Invalid user ID")])

        account = self._user_repository.find_account_by_user_id(user_id)
        if account is None:
            return Result.fail([UserNotExistError("User not found")])

        if not self._hash_service.verify(parameters.current_password, account.password.passphrase):
            return Result.fail([WrongPasswordError("Current password is incorrect")])

        from src.domain.value_objects import PlaintextPassword, HashedPassword
        new_pw_validation = PlaintextPassword.validate(passphrase=parameters.new_password)
        if new_pw_validation.is_failure:
            return new_pw_validation

        hashed_new = self._hash_service.hash(parameters.new_password)
        account._password = HashedPassword(passphrase=hashed_new)
        self._user_repository.update_account(account)

        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: ChangePasswordData,
    ) -> Result[bool, list[DomainError]]:
        from src.domain.value_objects import PlaintextPassword
        new_pw = PlaintextPassword.validate(passphrase=parameters.new_password)
        return new_pw
