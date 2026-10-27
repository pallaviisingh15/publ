from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.models.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"), nullable=False)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))

    customer: Mapped["Customer"] = relationship(back_populates="purchase_orders")  # noqa: F821
    publication: Mapped["Publication"] = relationship(back_populates="purchase_orders")  # noqa: F821
