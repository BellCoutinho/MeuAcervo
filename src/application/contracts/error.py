from typing import Self


class UseCaseError(Exception):
    def __init__(self: Self, message: str) -> None:
        super().__init__(f'UseCaseError :: {message}')
