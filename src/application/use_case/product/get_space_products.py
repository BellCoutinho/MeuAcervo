from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import SpaceNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductRepository


class GetSpaceProductsData(NamedTuple):
    user_id: str
    space_id: str
    term: str | None = None
    category: str | None = None
    warranty_status: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    sort_by: str | None = None
    sort_order: str = "desc"
    limit: int = 50
    offset: int = 0


class GetSpaceProducts(UseCase):
    def __init__(
        self: Self,
        product_repository: ProductRepository,
    ) -> None:
        self._product_repository = product_repository

    def perform(
        self: Self,
        parameters: GetSpaceProductsData,
    ) -> Result[list[dict], list[DomainError | SpaceNotExistsError]]:
        from uuid import UUID
        try:
            space_id = UUID(parameters.space_id)
        except ValueError:
            return Result.fail([SpaceNotExistsError("Invalid space ID")])

        products = self._product_repository.search(
            space_id=space_id,
            term=parameters.term,
            category=parameters.category,
            warranty_status=parameters.warranty_status,
            min_value=parameters.min_value,
            max_value=parameters.max_value,
            sort_by=parameters.sort_by,
            sort_order=parameters.sort_order,
            limit=parameters.limit,
            offset=parameters.offset,
        )

        products_list = []
        for p in products:
            products_list.append({
                "product_id": str(p.id),
                "name": p.name.name,
                "category": p.category.category.value,
                "brand": p.brand.brand,
                "model": p.model.model,
                "purchase_value": p.purchase_value.value,
                "warranty_status": p.warranty_status,
                "status": p.status,
            })

        return Result.ok(products_list)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: GetSpaceProductsData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
