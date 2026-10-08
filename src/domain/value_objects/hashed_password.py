from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from src.domain.errors import HashLengthError, MissingParameterError
from src.domain.value_objects.ports import Password
from src.shared.result import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError


class HashedPassword(Password):
    def __init__(self: Self, passphrase: str) -> None:
        self._hashed_passphrase = passphrase

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, HashedPassword):
            return False
        return other.passphrase == self._hashed_passphrase

    @property
    def passphrase(self: Self) -> str:
        return self._hashed_passphrase

    @classmethod
    def create(
        cls: type[HashedPassword], **kwargs: dict[str, Any],
    ) -> Result[Self, list[DomainError]]:
        hashed_passphrase = kwargs.get("passphrase")
        hashed_passphrase_validation_result = cls.validate(passphrase=hashed_passphrase)
        if hashed_passphrase_validation_result.is_failure:
            return hashed_passphrase_validation_result
        return Result.ok(HashedPassword(
            passphrase=hashed_passphrase,
        ))

    @classmethod
    def validate(
        cls: type["HashedPassword"], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        hashed_passphrase = kwargs.get("passphrase")
        errors = []
        if hashed_passphrase is None or len(str(hashed_passphrase).strip()) == 0:
            errors.append(MissingParameterError("passphrase"))
            return Result.fail(errors)
        return Result.ok(value=True)
