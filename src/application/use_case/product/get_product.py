from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import ProductNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductFileRepository, ProductRepository


class GetProductData(NamedTuple):
    user_id: str
    product_id: str


class GetProduct(UseCase):
    def __init__(
        self: Self,
        product_repository: ProductRepository,
        file_repository: ProductFileRepository,
    ) -> None:
        self._product_repository = product_repository
        self._file_repository = file_repository

    def perform(
        self: Self,
        parameters: GetProductData,
    ) -> Result[dict, list[DomainError | ProductNotExistsError]]:
        from uuid import UUID
        try:
            product_id = UUID(parameters.product_id)
        except ValueError:
            return Result.fail([ProductNotExistsError("Invalid product ID")])

        product = self._product_repository.find_by_id(product_id)
        if product is None:
            return Result.fail([ProductNotExistsError("Product not found")])

        files = self._file_repository.find_by_product_id(product_id)
        files_list = []
        for f in files:
            files_list.append({
                "file_id": str(f.id),
                "file_name": f.file_name,
                "file_type": f.file_type.file_type.value,
                "file_size": f.file_size.size,
            })

        return Result.ok({
            "product_id": str(product.id),
            "name": product.name.name,
            "category": product.category.category.value,
            "brand": product.brand.brand,
            "model": product.model.model,
            "location": product.location.location,
            "purchase_value": product.purchase_value.value,
            "serial_number": product.serial_number.serial_number,
            "warranty_type": product.warranty_type,
            "warranty_status": product.warranty_status,
            "status": product.status,
            "files": files_list,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: GetProductData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
