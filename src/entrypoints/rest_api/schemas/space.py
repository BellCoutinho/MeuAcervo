from pydantic import BaseModel


class UpdateSpaceRequest(BaseModel):
    name: str | None = None
    address: str | None = None
    utility_unit_number: str | None = None
    storage_quota: int | None = None
