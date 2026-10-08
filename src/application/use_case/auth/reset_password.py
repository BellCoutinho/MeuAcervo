from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import InvalidTokenError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import HashService
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class ResetPasswordData(NamedTuple):
    token: str
    new_password: str


class ResetPassword(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
        hash_service: HashService,
    ) -> None:
        self._user_repository = user_repository
        self._hash_service = hash_service

    def perform(
        self: Self,
        parameters: ResetPasswordData,
    ) -> Result[bool, list[DomainError | InvalidTokenError]]:
        validation_result = ResetPassword.validate_parameters(parameters)
        if validation_result.is_failure:
            return validation_result

        account = self._user_repository.find_account_by_reset_token(parameters.token)
        if account is None:
            return Result.fail([InvalidTokenError("Invalid or expired reset token")])

        if account.reset_token_expiry:
            expiry = datetime.fromisoformat(account.reset_token_expiry)
            if datetime.now() > expiry:
                return Result.fail([InvalidTokenError("Reset token has expired")])

        from src.domain.value_objects import HashedPassword
        hashed = self._hash_service.hash(parameters.new_password)
        account._password = HashedPassword(passphrase=hashed)
        account._reset_token = None
        account._reset_token_expiry = None
        self._user_repository.update_account(account)

        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: ResetPasswordData,
    ) -> Result[bool, list[DomainError]]:
        if not parameters.token:
            return Result.fail([InvalidTokenError("Token is required")])
        from src.domain.value_objects import PlaintextPassword
        return PlaintextPassword.validate(passphrase=parameters.new_password)
