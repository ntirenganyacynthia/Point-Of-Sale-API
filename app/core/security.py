from datetime import datetime, timedelta, timezone

import jwt
from cryptography.fernet import Fernet
from pwdlib import PasswordHash

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    MFA_ENCRYPTION_KEY,
)


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(subject_id: int, token_type: str = "user") -> str:
    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(subject_id),
        "type": token_type,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_customer_access_token(customer_id: int) -> str:
    return create_access_token(customer_id, token_type="customer")


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )


def encrypt_mfa_secret(secret: str) -> str:
    if not MFA_ENCRYPTION_KEY:
        raise RuntimeError(
            "MFA_ENCRYPTION_KEY is not configured."
        )

    cipher = Fernet(
        MFA_ENCRYPTION_KEY.encode()
    )

    return cipher.encrypt(
        secret.encode()
    ).decode()


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    if not MFA_ENCRYPTION_KEY:
        raise RuntimeError(
            "MFA_ENCRYPTION_KEY is not configured."
        )

    cipher = Fernet(
        MFA_ENCRYPTION_KEY.encode()
    )

    return cipher.decrypt(
        encrypted_secret.encode()
    ).decode()