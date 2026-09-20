from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sale_id = Column(
        Integer,
        ForeignKey("sales.sale_id"),
        nullable=False
    )

    payment_method = Column(
        String(50),
        nullable=False
    )

    amount_paid = Column(
        Numeric(10, 2),
        nullable=False
    )

    payment_status = Column(
        String(50),
        nullable=False,
        default="pending"
    )

    payment_date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    sale = relationship(
        "Sale",
        back_populates="payments"
    )