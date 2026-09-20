from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class PaymentBase(BaseModel):
    sale_id: int = Field(gt=0)

    payment_method: str = Field(
        min_length=1,
        max_length=50
    )

    amount_paid: Decimal = Field(
        gt=0
    )


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_method: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    payment_status: str | None = None


class PaymentRead(PaymentBase):
    payment_id: int
    payment_status: str
    payment_date: datetime
    model_config = ConfigDict(from_attributes=True)