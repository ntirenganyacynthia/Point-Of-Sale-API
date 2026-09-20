from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.receipt import (
    ReceiptCreate,
    ReceiptRead,
    ReceiptUpdate
)

from app.services.receipt import (
    get_all_receipts,
    get_receipt,
    create_receipt,
    update_receipt,
    delete_receipt
)

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"]
)


@router.get("/", response_model=list[ReceiptRead])
def read_receipts(
    db: Session = Depends(get_db)
):
    return get_all_receipts(db)


@router.get("/{receipt_id}", response_model=ReceiptRead)
def read_receipt(
    receipt_id: int,
    db: Session = Depends(get_db)
):
    return get_receipt(db, receipt_id)


@router.post(
    "/",
    response_model=ReceiptRead,
    status_code=status.HTTP_201_CREATED
)
def add_receipt(
    receipt: ReceiptCreate,
    db: Session = Depends(get_db)
):
    return create_receipt(db, receipt)


@router.put(
    "/{receipt_id}",
    response_model=ReceiptRead
)
def edit_receipt(
    receipt_id: int,
    receipt: ReceiptUpdate,
    db: Session = Depends(get_db)
):
    return update_receipt(
        db,
        receipt_id,
        receipt
    )


@router.delete(
    "/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_receipt(
    receipt_id: int,
    db: Session = Depends(get_db)
):
    delete_receipt(
        db,
        receipt_id
    )