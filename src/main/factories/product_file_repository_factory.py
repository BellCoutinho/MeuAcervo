from src.infrastructure.repositories.postgresql_product_file_repository import ProductFilePostgreSQLRepository
from src.domain.repositories import ProductFileRepository


def make_product_file_repository() -> ProductFileRepository:
    return ProductFilePostgreSQLRepository()
