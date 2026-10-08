from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import SpaceNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductRepository


class RegisterProductData(NamedTuple):
    user_id: str
    space_id: str
    name: str
    category: str
    brand: str
    model: str
    location: str
    purchase_value: float
    purchase_date: str | None = None
    serial_number: str | None = None
    warranty_type: str | None = None
    warranty_expiry: str | None = None
    extended_warranty_expiry: str | None = None


class RegisterProduct(UseCase):
    def __init__(
        self: Self,
        product_repository: ProductRepository,
    ) -> None:
        self._product_repository = product_repository

    def perform(
        self: Self,
        parameters: RegisterProductData,
    ) -> Result[dict, list[DomainError | SpaceNotExistsError]]:
        validation_result = RegisterProduct.validate_parameters(parameters)
        if validation_result.is_failure:
            return validation_result

        from uuid import UUID
        from src.domain.entities import Product

        product_result = Product.create(
            name=parameters.name,
            category=parameters.category,
            brand=parameters.brand,
            model=parameters.model,
            location=parameters.location,
            purchase_value=parameters.purchase_value,
            purchase_date=parameters.purchase_date,
            serial_number=parameters.serial_number,
            warranty_type=parameters.warranty_type,
            warranty_expiry=parameters.warranty_expiry,
            extended_warranty_expiry=parameters.extended_warranty_expiry,
            user_id=UUID(parameters.user_id),
            space_id=UUID(parameters.space_id),
        )
        if product_result.is_failure:
            return product_result

        product = product_result.value
        self._product_repository.add(product)

        return Result.ok({
            "product_id": str(product.id),
            "name": parameters.name,
            "warranty_status": product.warranty_status,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: RegisterProductData,
    ) -> Result[bool, list[DomainError]]:
        from src.domain.entities import Product
        return Product.validate(
            name=parameters.name,
            category=parameters.category,
            brand=parameters.brand,
            model=parameters.model,
            location=parameters.location,
            purchase_value=parameters.purchase_value,
        )
