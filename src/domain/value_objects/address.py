from __future__ import annotations

from typing import Any, Self

from src.domain.errors import (
    MissingParameterError,
    TooLongAddressError,
    TooShortAddressError,
)
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Address(ValueObject):
    MINIMUM_LENGTH: int = 5
    MAXIMUM_LENGTH: int = 200

    def __init__(self: Self, address: str) -> None:
        self._address = address

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Address):
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
        validation = cls.validate(address=address)
        if validation.is_failure:
            return validation
        return Result.ok(Address(address))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        address = kwargs.get("address")
        errors = []
        if address is None:
            errors.append(MissingParameterError("address"))
            return Result.fail(errors)
        if len(address) < cls.MINIMUM_LENGTH:
            errors.append(TooShortAddressError())
        if len(address) > cls.MAXIMUM_LENGTH:
            errors.append(TooLongAddressError())
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
