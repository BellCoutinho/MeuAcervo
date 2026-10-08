from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Self

from src.domain.errors import (
    MissingNumberPasswordError,
    MissingParameterError,
    MissingSpecialCharacterPasswordError,
    TooLongPasswordError,
    WeakPasswordError,
)
from src.domain.value_objects.ports import Password
from src.shared.result import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError


class PlaintextPassword(Password):
    MINIMUM_PASSWORD_LENGTH: int = 8
    MAXIMUM_PASSWORD_LENGTH: int = 64

    def __init__(self: Self, passphrase: str) -> None:
        self._passphrase = passphrase

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Password):
            return False
        return other.passphrase == self._passphrase

    @property
    def passphrase(self: Self) -> str:
        return self._passphrase

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any],
    ) -> Result[Self, list[DomainError]]:
        passphrase = kwargs.get("passphrase")
        password_validation_result = cls.validate(passphrase=passphrase)
        if password_validation_result.is_failure:
            return password_validation_result
        return Result.ok(PlaintextPassword(
            passphrase=passphrase,
        ))

    @classmethod
    def validate(
        cls: type["Password"], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        passphrase = kwargs.get("passphrase")
        errors = []
        if passphrase is None:
            errors.append(MissingParameterError("passphrase"))
            return Result.fail(errors)
        if len(passphrase) < PlaintextPassword.MINIMUM_PASSWORD_LENGTH:
            errors.append(WeakPasswordError())
        if len(passphrase) > PlaintextPassword.MAXIMUM_PASSWORD_LENGTH:
            errors.append(TooLongPasswordError())
        if bool(re.search(r"[!@#$%^&*?]", passphrase)) is False:
            errors.append(MissingSpecialCharacterPasswordError())
        if bool(re.search(r"\d", passphrase)) is False:
            errors.append(MissingNumberPasswordError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
