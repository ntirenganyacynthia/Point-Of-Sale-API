from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    mfa_enabled = Column(
        Boolean,
        nullable=False,
        default=False
    )

    mfa_secret = Column(
        String(500),
        nullable=True
    )

    sales = relationship(
        "Sale",
        back_populates="user"
    )