from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.sale_item import (
    SaleItemCreate,
    SaleItemRead,
    SaleItemUpdate
)

from app.services.sale_item import (
    get_all_sale_items,
    get_sale_item,
    create_sale_item,
    update_sale_item,
    delete_sale_item
)

router = APIRouter(
    prefix="/sale-items",
    tags=["Sale Items"]
)


@router.get("/", response_model=list[SaleItemRead])
def read_sale_items(
    db: Session = Depends(get_db)
):
    return get_all_sale_items(db)


@router.get("/{sale_item_id}", response_model=SaleItemRead)
def read_sale_item(
    sale_item_id: int,
    db: Session = Depends(get_db)
):
    return get_sale_item(db, sale_item_id)


@router.post(
    "/",
    response_model=SaleItemRead,
    status_code=status.HTTP_201_CREATED
)
def add_sale_item(
    sale_item: SaleItemCreate,
    db: Session = Depends(get_db)
):
    return create_sale_item(db, sale_item)


@router.put(
    "/{sale_item_id}",
    response_model=SaleItemRead
)
def edit_sale_item(
    sale_item_id: int,
    sale_item: SaleItemUpdate,
    db: Session = Depends(get_db)
):
    return update_sale_item(
        db,
        sale_item_id,
        sale_item
    )


@router.delete(
    "/{sale_item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_sale_item(
    sale_item_id: int,
    db: Session = Depends(get_db)
):
    delete_sale_item(
        db,
        sale_item_id
    )