from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.errors import DomainError

from src.domain.contracts import Entity
from src.domain.value_objects import Date, Email, HashedPassword, UniqueId
from src.shared import Result


class Account(Entity):
    def __init__(
        self: Self,
        email: Email,
        password: HashedPassword,
        id: UniqueId | None = None,
        created_at: Date | None = None,
        is_active: bool = True,
        reset_token: str | None = None,
        reset_token_expiry: str | None = None,
        user_id: UUID | None = None,
    ) -> None:
        self._email = email
        self._password = password
        self._unique_id = id or UniqueId()
        self._created_at = created_at or Date()
        self._is_active = is_active
        self._reset_token = reset_token
        self._reset_token_expiry = reset_token_expiry
        self._user_id = user_id

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Account):
            return False
        return other.id == self._unique_id

    @property
    def id(self: Self) -> UUID:
        return self._unique_id.identifier

    @property
    def email(self: Self) -> Email:
        return self._email

    @property
    def password(self: Self) -> HashedPassword:
        return self._password

    @property
    def created_at(self: Self) -> Date:
        return self._created_at

    @property
    def is_active(self: Self) -> bool:
        return self._is_active

    @property
    def reset_token(self: Self) -> str | None:
        return self._reset_token

    @property
    def reset_token_expiry(self: Self) -> str | None:
        return self._reset_token_expiry

    @property
    def user_id(self: Self) -> UUID | None:
        return self._user_id

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        email_result = Email.create(address=kwargs.get("email"))
        password_result = HashedPassword.create(passphrase=kwargs.get("password"))
        id = kwargs.get("id")
        id_result = UniqueId.create(id=id) if id is not None else UniqueId.create()

        validation_result = Result.combine(email_result, password_result, id_result)
        if validation_result.is_failure:
            return validation_result
        return Result.ok(Account(
            email=email_result.value,
            password=password_result.value,
            id=id_result.value,
            is_active=kwargs.get("is_active", True),
            reset_token=kwargs.get("reset_token"),
            reset_token_expiry=kwargs.get("reset_token_expiry"),
            user_id=kwargs.get("user_id"),
        ))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        email_result = Email.validate(address=kwargs.get("email"))
        password_result = HashedPassword.validate(passphrase=kwargs.get("password"))
        return Result.combine(email_result, password_result)
