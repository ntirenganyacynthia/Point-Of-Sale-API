from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import get_current_customer
from app.schemas.customer import (
    CustomerCreate,
    CustomerLogin,
    CustomerRead,
    CustomerUpdate,
)
from app.services.customer import (
    create_customer,
    delete_customer,
    get_all_customers,
    get_customer,
    login_customer,
    register_customer,
    update_customer,
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/me", response_model=CustomerRead)
def read_current_customer(
    current_customer=Depends(get_current_customer),
):
    return current_customer


@router.get("/", response_model=list[CustomerRead])
def read_customers(
    db: Session = Depends(get_db)
):
    return get_all_customers(db)


@router.get("/{customer_id}", response_model=CustomerRead)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return get_customer(db, customer_id)


@router.post(
    "/register",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED
)
def add_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    return register_customer(db, customer)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
def login_customer_endpoint(
    customer: CustomerLogin,
    db: Session = Depends(get_db)
):
    return login_customer(
        db,
        customer.customer_email,
        customer.password,
    )


@router.post(
    "/",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED
)
def add_customer_record(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    return create_customer(db, customer)


@router.put(
    "/{customer_id}",
    response_model=CustomerRead
)
def edit_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db)
):
    return update_customer(
        db,
        customer_id,
        customer
    )


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    delete_customer(
        db,
        customer_id
    )