from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.payment import (
    PaymentCreate,
    PaymentRead,
    PaymentUpdate
)

from app.services.payment import (
    get_all_payments,
    get_payment,
    create_payment,
    update_payment,
    delete_payment
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.get("/", response_model=list[PaymentRead])
def read_payments(
    db: Session = Depends(get_db)
):
    return get_all_payments(db)


@router.get("/{payment_id}", response_model=PaymentRead)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    return get_payment(db, payment_id)


@router.post(
    "/",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED
)
def add_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    return create_payment(db, payment)


@router.put(
    "/{payment_id}",
    response_model=PaymentRead
)
def edit_payment(
    payment_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(get_db)
):
    return update_payment(
        db,
        payment_id,
        payment
    )


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    delete_payment(
        db,
        payment_id
    )