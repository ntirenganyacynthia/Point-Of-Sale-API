from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.sale import (
    SaleCreate,
    SaleRead,
    SaleUpdate
)

from app.services.sale import (
    get_all_sales,
    get_sale,
    create_sale,
    update_sale,
    delete_sale
)

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)


@router.get("/", response_model=list[SaleRead])
def read_sales(db: Session = Depends(get_db)):
    return get_all_sales(db)


@router.get("/{sale_id}", response_model=SaleRead)
def read_sale(
    sale_id: int,
    db: Session = Depends(get_db)
):
    return get_sale(db, sale_id)


@router.post(
    "/",
    response_model=SaleRead,
    status_code=status.HTTP_201_CREATED
)
def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
):
    return create_sale(db, sale)


@router.put(
    "/{sale_id}",
    response_model=SaleRead
)
def edit_sale(
    sale_id: int,
    sale: SaleUpdate,
    db: Session = Depends(get_db)
):
    return update_sale(
        db,
        sale_id,
        sale
    )


@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_sale(
    sale_id: int,
    db: Session = Depends(get_db)
):
    delete_sale(
        db,
        sale_id
    )