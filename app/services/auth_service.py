from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import base64
import io
import jwt
import pyotp
import qrcode

from jwt import InvalidTokenError

from app.core.config import (
    ALGORITHM,
    SECRET_KEY,
)

from app.core.security import (
    create_access_token,
    verify_password,
    encrypt_mfa_secret,
    decrypt_mfa_secret,
)

from app.models.user import User
from app.repositories.user import user_repository


def authenticate_user(
    db: Session,
    username: str,
    password: str
):
    user = user_repository.get_by_username(
        db,
        username
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return user


def login(
    db: Session,
    username: str,
    password: str
):
    user = authenticate_user(
        db,
        username,
        password
    )

    if user.mfa_enabled:
        return {
            "mfa_required": True,
            "user_id": user.user_id
        }

    return {
        "mfa_required": False,
        "access_token": create_access_token(
            user.user_id
        ),
        "token_type": "bearer"
    }


def setup_mfa(
    db: Session,
    user: User
):
    if user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled."
        )


    secret = pyotp.random_base32()


    user.mfa_secret = encrypt_mfa_secret(
        secret
    )


    user.mfa_enabled = False

    db.commit()
    db.refresh(user)

 
    totp = pyotp.TOTP(secret)

    provisioning_uri = totp.provisioning_uri(
        name=user.username,
        issuer_name="POS System"
    )

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    qr_image = qr.make_image()


    buffer = io.BytesIO()

    qr_image.save(
        buffer,
        format="PNG"
    )

  
    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return {
        "message": "MFA setup initialized.",
        "qr_code": f"data:image/png;base64,{qr_base64}"
    }


def verify_mfa(
    db: Session,
    user: User,
    code: str
):
    if not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA has not been configured."
        )

  
    secret = decrypt_mfa_secret(
        user.mfa_secret
    )

    totp = pyotp.TOTP(secret)

 
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code."
        )

   
    user.mfa_enabled = True

    db.commit()
    db.refresh(user)

    return create_access_token(
        user.user_id
    )


def verify_token(
    db: Session,
    token: str
):
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
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if payload.get("type") not in (None, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user = (
        db.query(User)
        .filter(
            User.user_id == int(user_id)
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return user