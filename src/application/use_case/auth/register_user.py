from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, NamedTuple, Self

from src.domain.entities import Account, Space, User
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import HashService, TokenManager
    from src.domain.contracts import DomainError
    from src.domain.repositories import SpaceRepository, UserRepository

from src.application.use_case.errors import UserAlreadyExistsError
from src.application.contracts import UseCase


class RegistrationData(NamedTuple):
    first_name: str
    last_name: str
    email: str
    password: str
    space_name: str
    space_address: str
    utility_unit_number: str


class RegisterUser(UseCase):
    def __init__(
        self: Self,
        user_repository: UserRepository,
        space_repository: SpaceRepository,
        hash_service: HashService,
    ) -> None:
        self._user_repository = user_repository
        self._space_repository = space_repository
        self._hash_service = hash_service

    def perform(
        self: Self,
        parameters: RegistrationData,
    ) -> Result[dict, list[DomainError | UserAlreadyExistsError]]:
        validation_result = RegisterUser.validate_parameters(parameters)
        if validation_result.is_failure:
            return validation_result

        if self._user_repository.exist_by_email(parameters.email):
            return Result.fail(
                [UserAlreadyExistsError(f'The user with email "{parameters.email}" already exists')]
            )

        space_result = Space.create(
            name=parameters.space_name,
            address=parameters.space_address,
            utility_unit_number=parameters.utility_unit_number,
        )
        if space_result.is_failure:
            return space_result

        space = space_result.value
        self._space_repository.add(space)

        hashed_password = self._hash_service.hash(parameters.password)
        account_result = Account.create(
            email=parameters.email,
            password=hashed_password,
        )
        if account_result.is_failure:
            return account_result

        user_result = User.create(
            first_name=parameters.first_name,
            last_name=parameters.last_name,
            role="admin",
            is_approved=True,
            space_id=space.id,
        )
        if user_result.is_failure:
            return user_result

        user = user_result.value
        account = account_result.value
        account._user_id = user.id
        self._user_repository.add(user, account)

        return Result.ok({
            "user_id": str(user.id),
            "space_id": str(space.id),
            "email": parameters.email,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: RegistrationData,
    ) -> Result[bool, list[DomainError]]:
        user_validation = User.validate(
            first_name=parameters.first_name,
            last_name=parameters.last_name,
        )
        account_validation = Account.validate(
            email=parameters.email,
            password=parameters.password,
        )
        space_validation = Space.validate(
            name=parameters.space_name,
            address=parameters.space_address,
            utility_unit_number=parameters.utility_unit_number,
        )
        return Result.combine(user_validation, account_validation, space_validation)
