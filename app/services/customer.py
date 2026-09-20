from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import jwt
from jwt import InvalidTokenError

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.security import (
    create_customer_access_token,
    hash_password,
    verify_password,
)
from app.repositories.customer import customer_repository


def get_all_customers(db: Session):
    return customer_repository.get_all(db)


def get_customer(db: Session, customer_id: int):
    customer = customer_repository.get_by_id(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )

    return customer


def register_customer(db: Session, customer):
    email = customer.customer_email.strip().lower()
    phone = customer.customer_phonenumber.strip() if customer.customer_phonenumber else None

    if customer_repository.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A customer with this email already exists."
        )

    if phone and customer_repository.get_by_phone(db, phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A customer with this phone number already exists."
        )

    data = {
        "full_name": customer.full_name.strip(),
        "customer_email": email,
        "customer_phonenumber": phone,
        "password_hash": hash_password(customer.password),
        "is_active": True,
    }

    return customer_repository.create(db, data)


def create_customer(db: Session, customer):
    return register_customer(db, customer)


def authenticate_customer(db: Session, customer_email: str, password: str):
    email = customer_email.strip().lower()
    customer = customer_repository.get_by_email(db, email)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer account is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return customer


def login_customer(db: Session, customer_email: str, password: str):
    customer = authenticate_customer(db, customer_email, password)

    return {
        "access_token": create_customer_access_token(customer.customer_id),
        "token_type": "bearer",
        "customer_id": customer.customer_id,
    }


def verify_customer_token(db: Session, token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid customer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer_id = payload.get("sub")
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid customer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer = customer_repository.get_by_id(db, int(customer_id))
    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer account is not active.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return customer


def update_customer(
    db: Session,
    customer_id: int,
    customer
):
    db_customer = get_customer(db, customer_id)
    data = customer.model_dump(exclude_unset=True)

    if "customer_email" in data:
        email = data["customer_email"].strip().lower()
        if customer_repository.get_by_email(db, email) and email != db_customer.customer_email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A customer with this email already exists."
            )
        data["customer_email"] = email

    if "customer_phonenumber" in data and data["customer_phonenumber"] is not None:
        phone = data["customer_phonenumber"].strip()
        if customer_repository.get_by_phone(db, phone) and phone != db_customer.customer_phonenumber:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A customer with this phone number already exists."
            )
        data["customer_phonenumber"] = phone

    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))

    return customer_repository.update(db, db_customer, data)


def delete_customer(
    db: Session,
    customer_id: int
):
    db_customer = get_customer(db, customer_id)
    customer_repository.delete(db, db_customer)