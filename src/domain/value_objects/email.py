from __future__ import annotations

from typing import Any, Self

from src.domain.errors import (
    MissingAtSignEmailError,
    MissingParameterError,
    TooLongDomainEmailError,
    TooLongLocalPartEmailError,
    TooShortDomainEmailError,
    TooShortLocalPartEmailError,
)
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Email(ValueObject):
    MINIMUM_LOCAL_PART_LENGTH: int = 3
    MAXIMUM_LOCAL_PART_LENGTH: int = 64
    MINIMUM_DOMAIN_PART_LENGTH: int = 3
    MAXIMUM_DOMAIN_PART_LENGTH: int = 254

    def __init__(self: Self, address: str) -> None:
        self._address = address

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Email):
            return False
        return other.address == self._address

    @property
    def address(self: Self) -> str:
        return self._address

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        address = kwargs.get("address")
        email_validation_result = cls.validate(address=address)
        if email_validation_result.is_failure:
            return email_validation_result
        return Result.ok(Email(address))

    @classmethod
    def validate(
        cls: type["Email"],
        **kwargs: dict[str, Any],
    ) -> Result[bool, list[Exception]]:
        address = kwargs.get("address")
        errors = []
        if address is None:
            errors.append(MissingParameterError("address"))
            return Result.fail(error=errors)
        if address.count("@") != 1:
            errors.append(MissingAtSignEmailError())
            return Result.fail(error=errors)
        local_part, domain = address.split("@")
        if len(local_part) < Email.MINIMUM_LOCAL_PART_LENGTH:
            errors.append(TooShortLocalPartEmailError())
        elif len(local_part) > Email.MAXIMUM_LOCAL_PART_LENGTH:
            errors.append(TooLongLocalPartEmailError())
        if len(domain) < Email.MINIMUM_DOMAIN_PART_LENGTH:
            errors.append(TooShortDomainEmailError())
        elif len(domain) > Email.MAXIMUM_DOMAIN_PART_LENGTH:
            errors.append(TooLongDomainEmailError())
        if len(errors) > 0:
            return Result.fail(error=errors)
        return Result.ok(value=True)
