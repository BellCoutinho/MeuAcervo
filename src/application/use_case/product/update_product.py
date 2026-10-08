from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import ProductNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductRepository


class UpdateProductData(NamedTuple):
    user_id: str
    product_id: str
    name: str | None = None
    category: str | None = None
    brand: str | None = None
    model: str | None = None
    location: str | None = None
    purchase_value: float | None = None
    purchase_date: str | None = None
    serial_number: str | None = None
    warranty_type: str | None = None
    warranty_expiry: str | None = None
    extended_warranty_expiry: str | None = None


class UpdateProduct(UseCase):
    def __init__(
        self: Self,
        product_repository: ProductRepository,
    ) -> None:
        self._product_repository = product_repository

    def perform(
        self: Self,
        parameters: UpdateProductData,
    ) -> Result[bool, list[DomainError | ProductNotExistsError]]:
        from uuid import UUID
        try:
            product_id = UUID(parameters.product_id)
        except ValueError:
            return Result.fail([ProductNotExistsError("Invalid product ID")])

        product = self._product_repository.find_by_id(product_id)
        if product is None:
            return Result.fail([ProductNotExistsError("Product not found")])

        if parameters.name:
            from src.domain.value_objects import ProductName
            r = ProductName.create(name=parameters.name)
            if r.is_failure:
                return r
            product._name = r.value

        if parameters.category:
            from src.domain.value_objects import Category
            r = Category.create(category=parameters.category)
            if r.is_failure:
                return r
            product._category = r.value

        if parameters.brand:
            from src.domain.value_objects import Brand
            r = Brand.create(brand=parameters.brand)
            if r.is_failure:
                return r
            product._brand = r.value

        if parameters.model:
            from src.domain.value_objects import Model
            r = Model.create(model=parameters.model)
            if r.is_failure:
                return r
            product._model = r.value

        if parameters.location:
            from src.domain.value_objects import Location
            r = Location.create(location=parameters.location)
            if r.is_failure:
                return r
            product._location = r.value

        if parameters.purchase_value is not None:
            from src.domain.value_objects import PurchaseValue
            r = PurchaseValue.create(value=parameters.purchase_value)
            if r.is_failure:
                return r
            product._purchase_value = r.value

        if parameters.serial_number is not None:
            from src.domain.value_objects import SerialNumber
            r = SerialNumber.create(serial_number=parameters.serial_number)
            if r.is_failure:
                return r
            product._serial_number = r.value

        if parameters.warranty_type is not None:
            product._warranty_type = parameters.warranty_type

        if parameters.warranty_expiry is not None:
            from src.domain.value_objects import WarrantyDate
            r = WarrantyDate.create(date=parameters.warranty_expiry)
            if r.is_success:
                product._warranty_expiry = r.value

        if parameters.extended_warranty_expiry is not None:
            from src.domain.value_objects import WarrantyDate
            r = WarrantyDate.create(date=parameters.extended_warranty_expiry)
            if r.is_success:
                product._extended_warranty_expiry = r.value

        self._product_repository.update(product)
        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: UpdateProductData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
