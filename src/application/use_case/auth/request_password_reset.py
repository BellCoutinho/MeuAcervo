from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import UserNotExistError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class RequestResetData(NamedTuple):
    email: str


class RequestPasswordReset(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    def perform(
        self: Self,
        parameters: RequestResetData,
    ) -> Result[dict, list[DomainError | UserNotExistError]]:
        validation_result = RequestPasswordReset.validate_parameters(parameters)
        if validation_result.is_failure:
            return validation_result

        account = self._user_repository.find_account_by_email(parameters.email)
        if account is None:
            return Result.ok({"message": "If the email exists, a reset link has been sent"})

        token = secrets.token_urlsafe(32)
        expiry = (datetime.now() + timedelta(hours=1)).isoformat()

        account._reset_token = token
        account._reset_token_expiry = expiry
        self._user_repository.update_account(account)

        return Result.ok({
            "message": "If the email exists, a reset link has been sent",
            "reset_token": token,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: RequestResetData,
    ) -> Result[bool, list[DomainError]]:
        from src.domain.value_objects import Email
        return Email.validate(address=parameters.email)
