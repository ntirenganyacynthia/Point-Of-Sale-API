from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SaleBase(BaseModel):

    customer_id: int
    user_id: int | None = None
    total_amount: Decimal
    sale_status: str


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):

    customer_id: int | None = None
    user_id: int | None = None
    total_amount: Decimal | None = None
    sale_status: str | None = None


class SaleRead(SaleBase):

    sale_id: int
    sale_date: datetime
    model_config = ConfigDict(from_attributes=True)