from src.infrastructure.repositories.postgresql_user_repository import UserPostgreSQLRepository
from src.domain.repositories import UserRepository


def make_user_repository() -> UserRepository:
    return UserPostgreSQLRepository()
