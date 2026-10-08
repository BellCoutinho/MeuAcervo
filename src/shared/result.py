from __future__ import annotations

from enum import Enum, auto
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class ResultStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()


class Result(Generic[T, E]):
    def __init__(
        self,
        status: ResultStatus,
        value: T | None = None,
        error: list[E] | None = None,
    ) -> None:
        self._status = status
        self._value = value
        self._error = error

    @property
    def value(self) -> T | None:
        return self._value

    @property
    def error(self) -> list[E] | None:
        return self._error

    @property
    def is_success(self) -> bool:
        return self._status == ResultStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        return self._status == ResultStatus.FAILURE

    @classmethod
    def ok(cls: type[Result[T, E]], value: T) -> Result[T, E]:
        return Result(ResultStatus.SUCCESS, value=value)

    @classmethod
    def fail(cls: type[Result[T, E]], error: list[E]) -> Result[T, E]:
        return Result(ResultStatus.FAILURE, error=error)

    @classmethod
    def combine(cls: type[Result[T, E]], *args: Result[T, E]) -> Result[bool, E]:
        errors: list[E] = []
        for result in args:
            if result.is_failure and result.error is not None:
                errors.extend(result.error)
        if errors:
            return Result(ResultStatus.FAILURE, error=errors)
        return Result(ResultStatus.SUCCESS, value=True)
