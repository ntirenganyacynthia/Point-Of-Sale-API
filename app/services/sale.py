from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product
from app.models.user import User
from app.repositories.sale import sale_repository


def get_all_sales(db: Session):
    return sale_repository.get_all(db)


def get_sale(db: Session, sale_id: int):
    sale = sale_repository.get_by_id(db, sale_id)

    if sale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found."
        )

    return sale


def create_sale(
    db: Session,
    sale,
    current_user=None
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == sale.customer_id
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )

    user_id = None

    if current_user is not None:
        user_id = current_user.user_id

    elif sale.user_id is not None:
        user = (
            db.query(User)
            .filter(
                User.user_id == sale.user_id
            )
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        user_id = user.user_id

    if sale.total_amount < Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total amount cannot be negative."
        )

    data = sale.model_dump()

    data["user_id"] = user_id

    return sale_repository.create(
        db,
        data
    )


def update_sale(
    db: Session,
    sale_id: int,
    sale
):
    db_sale = get_sale(
        db,
        sale_id
    )

    data = sale.model_dump(
        exclude_unset=True
    )

    if "total_amount" in data:
        if data["total_amount"] < Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total amount cannot be negative."
            )

    if "customer_id" in data:
        customer = (
            db.query(Customer)
            .filter(
                Customer.customer_id ==
                data["customer_id"]
            )
            .first()
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found."
            )

    if "user_id" in data and data["user_id"] is not None:
        user = (
            db.query(User)
            .filter(
                User.user_id == data["user_id"]
            )
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

    return sale_repository.update(
        db,
        db_sale,
        data
    )


def delete_sale(
    db: Session,
    sale_id: int
):
    db_sale = get_sale(
        db,
        sale_id
    )

    sale_repository.delete(
        db,
        db_sale
    )