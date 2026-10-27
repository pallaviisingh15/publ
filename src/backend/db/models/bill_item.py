from datetime import date
from decimal import Decimal
from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.models.base import Base


class BillItem(Base):
    __tablename__ = "bill_items"
    __table_args__ = (
        UniqueConstraint(
            "customer_id", "publication_id", "bill_date",
            name="uq_bill_item_per_month",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    bill_date: Mapped[date] = mapped_column(Date, nullable=False)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    discount: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="bill_items")  # noqa: F821
    publication: Mapped["Publication"] = relationship(back_populates="bill_items")  # noqa: F821
