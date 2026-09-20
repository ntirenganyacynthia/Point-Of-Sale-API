from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate
)

from app.services.product import (
    get_all_products,
    get_product,
    create_product,
    update_product,
    delete_product
)
from app.dependences import require_role

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get(
    "/",
    response_model=list[ProductRead]
)
def read_products(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "cashier")
    )
):
    return get_all_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductRead
)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "cashier")
    )
):
    return get_product(
        db,
        product_id
    )


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED
)
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):
    return create_product(
        db,
        product
    )


@router.put(
    "/{product_id}",
    response_model=ProductRead
)
def edit_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):
    return update_product(
        db,
        product_id,
        product
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin")
    )
):
    delete_product(
        db,
        product_id
    )