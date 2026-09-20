from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.repositories.payment import payment_repository


ALLOWED_PAYMENT_METHODS = {
    "mobile_money",
    "cash",
    "card"
}

ALLOWED_PAYMENT_STATUSES = {
    "pending",
    "completed",
    "failed"
}


def get_all_payments(db: Session):
    return payment_repository.get_all(db)


def get_payment(
    db: Session,
    payment_id: int
):
    payment = payment_repository.get_by_id(
        db,
        payment_id
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found."
        )

    return payment


def create_payment(
    db: Session,
    payment
):
    if payment.payment_method not in ALLOWED_PAYMENT_METHODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method."
        )

    if payment.amount_paid <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero."
        )

    sale = (
        db.query(Sale)
        .filter(
            Sale.sale_id == payment.sale_id
        )
        .first()
    )

    if sale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found."
        )

    if payment.amount_paid != sale.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must equal the sale total."
        )

    data = {
        "sale_id": payment.sale_id,
        "payment_method": payment.payment_method,
        "amount_paid": payment.amount_paid,
        "payment_status": "pending"
    }

    return payment_repository.create(
        db,
        data
    )


def update_payment(
    db: Session,
    payment_id: int,
    payment
):
    db_payment = get_payment(
        db,
        payment_id
    )

    data = payment.model_dump(
        exclude_unset=True
    )

    if "payment_status" in data:
        if data["payment_status"] not in ALLOWED_PAYMENT_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment status."
            )

    return payment_repository.update(
        db,
        db_payment,
        data
    )


def delete_payment(
    db: Session,
    payment_id: int
):
    db_payment = get_payment(
        db,
        payment_id
    )

    payment_repository.delete(
        db,
        db_payment
    )