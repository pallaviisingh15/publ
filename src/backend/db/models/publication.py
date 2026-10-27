import enum
from decimal import Decimal
from sqlalchemy import Enum as SQLEnum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.models.base import Base


class FrequencyEnum(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BI_ANNUAL = "bi_annual"
    ANNUAL = "annual"


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency: Mapped[FrequencyEnum] = mapped_column(SQLEnum(FrequencyEnum), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(  # noqa: F821
        back_populates="publication"
    )
    bill_items: Mapped[list["BillItem"]] = relationship(back_populates="publication")  # noqa: F821
