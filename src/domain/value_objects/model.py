from __future__ import annotations

from typing import Any, Self

from src.domain.errors import MissingParameterError
from src.domain.contracts import DomainError, ValueObject
from src.shared import Result


class Model(ValueObject):
    MINIMUM_LENGTH: int = 1
    MAXIMUM_LENGTH: int = 100

    def __init__(self: Self, model: str) -> None:
        self._model = model

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Model):
            return False
        return other.model == self._model

    @property
    def model(self: Self) -> str:
        return self._model

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        model = kwargs.get("model")
        validation = cls.validate(model=model)
        if validation.is_failure:
            return validation
        return Result.ok(Model(model))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        model = kwargs.get("model")
        errors = []
        if model is None or len(str(model).strip()) == 0:
            errors.append(MissingParameterError("model"))
            return Result.fail(errors)
        if len(model) < cls.MINIMUM_LENGTH or len(model) > cls.MAXIMUM_LENGTH:
            errors.append(MissingParameterError("model"))
        if len(errors) > 0:
            return Result.fail(errors)
        return Result.ok(value=True)
