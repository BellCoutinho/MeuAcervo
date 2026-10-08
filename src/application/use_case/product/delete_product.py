from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import ProductNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductRepository


class DeleteProductData(NamedTuple):
    user_id: str
    product_id: str
    reason: str


class DeleteProduct(UseCase):
    VALID_REASONS = ["sold", "broken", "stolen", "descarte"]

    def __init__(
        self: Self,
        product_repository: ProductRepository,
    ) -> None:
        self._product_repository = product_repository

    def perform(
        self: Self,
        parameters: DeleteProductData,
    ) -> Result[bool, list[DomainError | ProductNotExistsError]]:
        if parameters.reason not in self.VALID_REASONS:
            return Result.fail([ProductNotExistsError(
                f"Invalid reason. Must be one of: {', '.join(self.VALID_REASONS)}"
            )])

        from uuid import UUID
        try:
            product_id = UUID(parameters.product_id)
        except ValueError:
            return Result.fail([ProductNotExistsError("Invalid product ID")])

        product = self._product_repository.find_by_id(product_id)
        if product is None:
            return Result.fail([ProductNotExistsError("Product not found")])

        self._product_repository.update_status(product_id, "inactive", parameters.reason)
        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: DeleteProductData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
