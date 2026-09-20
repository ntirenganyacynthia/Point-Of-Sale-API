from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    customer_email: EmailStr
    customer_phonenumber: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )


class CustomerCreate(CustomerBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class CustomerLogin(BaseModel):
    customer_email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    customer_email: EmailStr | None = None
    customer_phonenumber: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )


class CustomerRead(CustomerBase):
    customer_id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)