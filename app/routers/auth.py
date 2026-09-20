from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, MFAVerifyRequest
from app.services.auth_service import (
    login,
    setup_mfa,
    verify_mfa,
    authenticate_user,
)
from app.dependences import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
def login_user(
    user: LoginRequest,
    db: Session = Depends(get_db)
):
    result = login(
        db,
        user.username,
        user.password
    )

    return result


@router.post(
    "/mfa/setup",
    status_code=status.HTTP_200_OK
)
def setup_mfa_endpoint(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return setup_mfa(
        db,
        current_user
    )


@router.post(
    "/mfa/verify",
    status_code=status.HTTP_200_OK
)
def verify_mfa_endpoint(
    data: MFAVerifyRequest,
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db,
        data.username,
        data.password
    )

    access_token = verify_mfa(
        db,
        user,
        data.code
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_my_account(
    current_user=Depends(get_current_user)
):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role,
        "mfa_enabled": current_user.mfa_enabled
    }