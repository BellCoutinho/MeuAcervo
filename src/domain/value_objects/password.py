from __future__ import annotations

from abc import abstractproperty
from typing import TYPE_CHECKING, Any, Self

from src.domain.contracts import DomainError, ValueObject

if TYPE_CHECKING:
    from src.shared.result import Result


class Password(ValueObject):

    @abstractproperty
    def passphrase(self: Self) -> str:
        raise NotImplementedError('Password: "passphrase" property should be implemented')

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any],
    ) -> Result[type[Password], list[DomainError]]:
        raise NotImplementedError("Password: Create method should be implemented")

    @classmethod
    def validate(
        cls: type["Password"], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        raise NotImplementedError("Password: Validate method should be implemented")
