from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import ProductNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductFileRepository, ProductRepository


class GetProductFilesData(NamedTuple):
    user_id: str
    product_id: str


class GetProductFiles(UseCase):
    def __init__(
        self: Self,
        file_repository: ProductFileRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._file_repository = file_repository
        self._product_repository = product_repository

    def perform(
        self: Self,
        parameters: GetProductFilesData,
    ) -> Result[list[dict], list[DomainError | ProductNotExistsError]]:
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

        return Result.ok(files_list)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: GetProductFilesData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
