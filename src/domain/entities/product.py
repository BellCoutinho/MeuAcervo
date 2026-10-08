from __future__ import annotations

from datetime import date
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.errors import DomainError

from src.domain.contracts import Entity
from src.domain.value_objects import (
    Brand,
    Category,
    Date,
    Location,
    Model,
    ProductName,
    PurchaseValue,
    SerialNumber,
    UniqueId,
    WarrantyDate,
)
from src.shared import Result


class ProductStatus(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()


class WarrantyType(StrEnum):
    MANUFACTURER = auto()
    EXTENDED = auto()


class Product(Entity):
    def __init__(
        self: Self,
        name: ProductName,
        category: Category,
        brand: Brand,
        model: Model,
        location: Location,
        purchase_value: PurchaseValue,
        id: UniqueId | None = None,
        purchase_date: Date | None = None,
        serial_number: SerialNumber | None = None,
        warranty_type: str | None = None,
        warranty_expiry: WarrantyDate | None = None,
        extended_warranty_expiry: WarrantyDate | None = None,
        status: str = "active",
        status_reason: str | None = None,
        user_id: UUID | None = None,
        space_id: UUID | None = None,
        created_at: Date | None = None,
    ) -> None:
        self._name = name
        self._category = category
        self._brand = brand
        self._model = model
        self._location = location
        self._purchase_value = purchase_value
        self._unique_id = id or UniqueId()
        self._purchase_date = purchase_date
        self._serial_number = serial_number
        self._warranty_type = warranty_type
        self._warranty_expiry = warranty_expiry
        self._extended_warranty_expiry = extended_warranty_expiry
        self._status = status
        self._status_reason = status_reason
        self._user_id = user_id
        self._space_id = space_id
        self._created_at = created_at or Date()

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Product):
            return False
        return other.id == self._unique_id

    @property
    def id(self: Self) -> UUID:
        return self._unique_id.identifier

    @property
    def name(self: Self) -> ProductName:
        return self._name

    @property
    def category(self: Self) -> Category:
        return self._category

    @property
    def brand(self: Self) -> Brand:
        return self._brand

    @property
    def model(self: Self) -> Model:
        return self._model

    @property
    def location(self: Self) -> Location:
        return self._location

    @property
    def purchase_value(self: Self) -> PurchaseValue:
        return self._purchase_value

    @property
    def purchase_date(self: Self) -> Date | None:
        return self._purchase_date

    @property
    def serial_number(self: Self) -> SerialNumber:
        return self._serial_number

    @property
    def warranty_type(self: Self) -> str | None:
        return self._warranty_type

    @property
    def warranty_expiry(self: Self) -> WarrantyDate | None:
        return self._warranty_expiry

    @property
    def extended_warranty_expiry(self: Self) -> WarrantyDate | None:
        return self._extended_warranty_expiry

    @property
    def status(self: Self) -> str:
        return self._status

    @property
    def status_reason(self: Self) -> str | None:
        return self._status_reason

    @property
    def user_id(self: Self) -> UUID | None:
        return self._user_id

    @property
    def space_id(self: Self) -> UUID | None:
        return self._space_id

    @property
    def created_at(self: Self) -> Date:
        return self._created_at

    @property
    def warranty_status(self: Self) -> str:
        if self._warranty_expiry and self._warranty_expiry.is_active:
            days = self._warranty_expiry.days_remaining
            return f"Ativa ({days} dias restantes)"
        if self._extended_warranty_expiry and self._extended_warranty_expiry.is_active:
            days = self._extended_warranty_expiry.days_remaining
            return f"Estendida ({days} dias restantes)"
        return "Expirada"

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        name_result = ProductName.create(name=kwargs.get("name"))
        category_result = Category.create(category=kwargs.get("category"))
        brand_result = Brand.create(brand=kwargs.get("brand"))
        model_result = Model.create(model=kwargs.get("model"))
        location_result = Location.create(location=kwargs.get("location"))
        pv_result = PurchaseValue.create(value=kwargs.get("purchase_value"))

        id = kwargs.get("id")
        id_result = UniqueId.create(id=id) if id is not None else UniqueId.create()

        sn_result = SerialNumber.create(serial_number=kwargs.get("serial_number"))

        warranty_expiry = kwargs.get("warranty_expiry")
        we_result = WarrantyDate.create(date=warranty_expiry) if warranty_expiry else Result.ok(WarrantyDate())

        ext_warranty = kwargs.get("extended_warranty_expiry")
        ewe_result = WarrantyDate.create(date=ext_warranty) if ext_warranty else Result.ok(WarrantyDate())

        validation_result = Result.combine(
            name_result, category_result, brand_result, model_result,
            location_result, pv_result, id_result, sn_result,
        )
        if validation_result.is_failure:
            return validation_result

        return Result.ok(Product(
            name=name_result.value,
            category=category_result.value,
            brand=brand_result.value,
            model=model_result.value,
            location=location_result.value,
            purchase_value=pv_result.value,
            id=id_result.value,
            purchase_date=Date.create(date=kwargs.get("purchase_date")).value if kwargs.get("purchase_date") else None,
            serial_number=sn_result.value,
            warranty_type=kwargs.get("warranty_type"),
            warranty_expiry=we_result.value if we_result.is_success else None,
            extended_warranty_expiry=ewe_result.value if ewe_result.is_success else None,
            status=kwargs.get("status", "active"),
            status_reason=kwargs.get("status_reason"),
            user_id=kwargs.get("user_id"),
            space_id=kwargs.get("space_id"),
        ))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        name_result = ProductName.validate(name=kwargs.get("name"))
        category_result = Category.validate(category=kwargs.get("category"))
        brand_result = Brand.validate(brand=kwargs.get("brand"))
        model_result = Model.validate(model=kwargs.get("model"))
        location_result = Location.validate(location=kwargs.get("location"))
        pv_result = PurchaseValue.validate(value=kwargs.get("purchase_value"))
        return Result.combine(
            name_result, category_result, brand_result, model_result,
            location_result, pv_result,
        )
