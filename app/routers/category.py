from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate
)

from app.services.category import (
    get_all_categories,
    get_category,
    create_category,
    update_category,
    delete_category
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "/",
    response_model=list[CategoryRead]
)
def read_categories(
    db: Session = Depends(get_db)
):
    return get_all_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryRead
)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    return get_category(
        db,
        category_id
    )


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED
)
def add_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    return create_category(
        db,
        category
    )


@router.put(
    "/{category_id}",
    response_model=CategoryRead
)
def edit_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    return update_category(
        db,
        category_id,
        category
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    delete_category(
        db,
        category_id
    )