from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self, overload

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.entities import Account, User
    from src.domain.value_objects import Role


class UserRepository(ABC):

    @overload
    @abstractmethod
    def exist_by_email(self: Self, email: str) -> bool:
        ...

    @overload
    @abstractmethod
    def exist_by_id(self: Self, id: UUID) -> bool:
        ...

    @abstractmethod
    def add(self: Self, user: User, account: Account) -> None:
        ...

    @abstractmethod
    def find_by_id(self: Self, id: UUID) -> User | None:
        ...

    @abstractmethod
    def find_by_email(self: Self, email: str) -> User | None:
        ...

    @abstractmethod
    def find_account_by_email(self: Self, email: str) -> Account | None:
        ...

    @abstractmethod
    def find_account_by_user_id(self: Self, user_id: UUID) -> Account | None:
        ...

    @abstractmethod
    def find_account_by_reset_token(self: Self, token: str) -> Account | None:
        ...

    @abstractmethod
    def find_role_by_id(self: Self, id: UUID) -> Role | None:
        ...

    @abstractmethod
    def find_all_by_space(self: Self, space_id: UUID) -> list[User]:
        ...

    @abstractmethod
    def update(self: Self, user: User) -> None:
        ...

    @abstractmethod
    def update_account(self: Self, account: Account) -> None:
        ...

    @abstractmethod
    def update_storage_used(self: Self, user_id: UUID, size: int) -> None:
        ...

    @abstractmethod
    def remove_by_id(self: Self, id: UUID) -> None:
        ...
