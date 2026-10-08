from src.infrastructure.repositories.postgresql_space_repository import SpacePostgreSQLRepository
from src.domain.repositories import SpaceRepository


def make_space_repository() -> SpaceRepository:
    return SpacePostgreSQLRepository()
