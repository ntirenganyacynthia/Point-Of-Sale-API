from decimal import Decimal

from pydantic import BaseModel, Field


class CheckoutItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0)


class CheckoutCreate(BaseModel):
    customer_id: int = Field(gt=0)

    items: list[CheckoutItem] = Field(
        min_length=1
    )

    payment_method: str = Field(
        min_length=1,
        max_length=50
    )


class CheckoutResponse(BaseModel):
    sale_id: int
    total_amount: Decimal
    payment_id: int
    payment_status: str
    receipt_id: int | None = None