import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pos.db")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key-change-me-in-production-please",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

MFA_ENCRYPTION_KEY = os.getenv(
    "MFA_ENCRYPTION_KEY",
    Fernet.generate_key().decode(),
)

MTN_MOMO_BASE_URL = os.getenv(
    "MTN_MOMO_BASE_URL",
    "https://sandbox.momodeveloper.mtn.com",
)

MTN_MOMO_SUBSCRIPTION_KEY = os.getenv("MTN_MOMO_SUBSCRIPTION_KEY")
MTN_MOMO_API_USER = os.getenv("MTN_MOMO_API_USER")
MTN_MOMO_API_KEY = os.getenv("MTN_MOMO_API_KEY")
MTN_MOMO_TARGET_ENVIRONMENT = os.getenv(
    "MTN_MOMO_TARGET_ENVIRONMENT",
    "sandbox",
)
MTN_MOMO_CURRENCY = os.getenv("MTN_MOMO_CURRENCY", "RWF")
