from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import get_current_user
from app.schemas.checkout import (
    CheckoutCreate,
    CheckoutResponse
)
from app.services.checkout import checkout


router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)


@router.post(
    "/",
    response_model=CheckoutResponse,
    status_code=status.HTTP_201_CREATED
)
def create_checkout(
    data: CheckoutCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return checkout(
        db,
        data,
        current_user
    )