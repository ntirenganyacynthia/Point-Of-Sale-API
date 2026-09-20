from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.repositories.receipt import receipt_repository


def get_all_receipts(db: Session):
    return receipt_repository.get_all(db)


def get_receipt(
    db: Session,
    receipt_id: int
):

    receipt = receipt_repository.get_by_id(
        db,
        receipt_id
    )

    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found."
        )

    return receipt


def create_receipt(
    db: Session,
    receipt
):

    sale = db.query(Sale).filter(
        Sale.sale_id == receipt.sale_id
    ).first()

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found."
        )

    try:
        return receipt_repository.create(
            db,
            receipt.model_dump()
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A receipt with this number or for this sale already exists."
        )


def update_receipt(
    db: Session,
    receipt_id: int,
    receipt
):

    db_receipt = get_receipt(
        db,
        receipt_id
    )

    try:
        return receipt_repository.update(
            db,
            db_receipt,
            receipt.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A receipt with this number already exists."
        )


def delete_receipt(
    db: Session,
    receipt_id: int
):

    db_receipt = get_receipt(
        db,
        receipt_id
    )

    receipt_repository.delete(
        db,
        db_receipt
    )