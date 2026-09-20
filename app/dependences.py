from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import auth_service
from app.services.customer import verify_customer_token


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    return auth_service.verify_token(
        db,
        credentials.credentials
    )


def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    return verify_customer_token(
        db,
        credentials.credentials
    )


def require_role(*allowed_roles):
    def role_checker(
        current_user = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )

        return current_user

    return role_checker