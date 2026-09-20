from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas.supplier import (
    SupplierCreate,
    SupplierRead,
    SupplierUpdate
)

from app.services.supplier import (
    get_all_suppliers,
    get_supplier,
    create_supplier,
    update_supplier,
    delete_supplier
)

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


@router.get("/", response_model=list[SupplierRead])
def read_suppliers(db: Session = Depends(get_db)):
    return get_all_suppliers(db)


@router.get("/{supplier_id}", response_model=SupplierRead)
def read_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    return get_supplier(
        db,
        supplier_id
    )


@router.post(
    "/",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED
)
def add_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db)
):
    return create_supplier(
        db,
        supplier
    )


@router.put(
    "/{supplier_id}",
    response_model=SupplierRead
)
def edit_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: Session = Depends(get_db)
):
    return update_supplier(
        db,
        supplier_id,
        supplier
    )


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    delete_supplier(
        db,
        supplier_id
    )