from pydantic import BaseModel


class RegisterProductRequest(BaseModel):
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


class UpdateProductRequest(BaseModel):
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


class DeactivateProductRequest(BaseModel):
    reason: str
