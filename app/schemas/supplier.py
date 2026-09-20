from pydantic import BaseModel, ConfigDict


class SupplierBase(BaseModel):
    supplier_name: str
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None


class SupplierRead(SupplierBase):
    supplier_id: int
    model_config = ConfigDict(from_attributes=True)