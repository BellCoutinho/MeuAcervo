from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import UserNotExistError, WrongPasswordError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import HashService, TokenManager
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class Credential(NamedTuple):
    email: str
    password: str


class LoginUseCase(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
        hash_service: HashService,
        token_manager: TokenManager,
    ) -> None:
        self._user_repository = user_repository
        self._hash_service = hash_service
        self._token_manager = token_manager

    def perform(
        self: Self,
        parameters: Credential,
    ) -> Result[dict, list[DomainError | UserNotExistError | WrongPasswordError]]:
        validation_result = LoginUseCase.validate_parameters(parameters)
        if validation_result.is_failure:
            return validation_result

        account = self._user_repository.find_account_by_email(parameters.email)
        if account is None:
            return Result.fail(
                [UserNotExistError(f'User with email "{parameters.email}" does not exist')]
            )

        if not self._hash_service.verify(parameters.password, account.password.passphrase):
            return Result.fail(
                [WrongPasswordError("Invalid password")]
            )

        user = self._user_repository.find_by_id(account.user_id)
        if user is None:
            return Result.fail(
                [UserNotExistError("User account is invalid")]
            )

        token = self._token_manager.create({
            "id": str(user.id),
            "email": parameters.email,
            "role": user.role.role_type.value,
        })

        return Result.ok({
            "access_token": token,
            "uid": str(user.id),
            "role": user.role.role_type.value,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: Credential,
    ) -> Result[bool, list[DomainError]]:
        from src.domain.value_objects import Email, PlaintextPassword
        email_result = Email.validate(address=parameters.email)
        password_result = PlaintextPassword.validate(passphrase=parameters.password)
        return Result.combine(email_result, password_result)
