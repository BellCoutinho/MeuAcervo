from src.infrastructure.repositories.postgresql_product_repository import ProductPostgreSQLRepository
from src.domain.repositories import ProductRepository


def make_product_repository() -> ProductRepository:
    return ProductPostgreSQLRepository()
