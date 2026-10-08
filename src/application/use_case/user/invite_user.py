from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import SpaceNotExistsError, UserAlreadyExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import HashService
    from src.domain.contracts import DomainError
    from src.domain.repositories import UserRepository


class InviteUserData(NamedTuple):
    admin_id: str
    space_id: str
    first_name: str
    last_name: str
    email: str
    password: str


class InviteUser(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
        hash_service: HashService,
    ) -> None:
        self._user_repository = user_repository
        self._hash_service = hash_service

    def perform(
        self: Self,
        parameters: InviteUserData,
    ) -> Result[dict, list[DomainError | UserAlreadyExistsError | SpaceNotExistsError]]:
        validation_result = InviteUser.validate_parameters(parameters)
        if validation_result.is_failure:
            return validation_result

        if self._user_repository.exist_by_email(parameters.email):
            return Result.fail(
                [UserAlreadyExistsError(f'User with email "{parameters.email}" already exists')]
            )

        from uuid import UUID
        space_id = UUID(parameters.space_id)

        hashed_password = self._hash_service.hash(parameters.password)
        from src.domain.entities import Account, User

        account_result = Account.create(
            email=parameters.email,
            password=hashed_password,
        )
        if account_result.is_failure:
            return account_result

        user_result = User.create(
            first_name=parameters.first_name,
            last_name=parameters.last_name,
            role="user",
            is_approved=False,
            space_id=space_id,
        )
        if user_result.is_failure:
            return user_result

        user = user_result.value
        account = account_result.value
        account._user_id = user.id
        self._user_repository.add(user, account)

        return Result.ok({
            "user_id": str(user.id),
            "email": parameters.email,
            "status": "pending_approval",
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: InviteUserData,
    ) -> Result[bool, list[DomainError]]:
        from src.domain.entities import User, Account
        user_validation = User.validate(
            first_name=parameters.first_name,
            last_name=parameters.last_name,
        )
        account_validation = Account.validate(
            email=parameters.email,
            password=parameters.password,
        )
        return Result.combine(user_validation, account_validation)
