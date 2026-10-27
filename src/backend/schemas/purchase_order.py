from datetime import date
from pydantic import BaseModel, ConfigDict, model_validator
from backend.schemas.customer import CustomerResponse
from backend.schemas.publication import PublicationResponse


class PurchaseOrderCreate(BaseModel):
    purchase_date: date
    customer_id: int
    publication_id: int
    sale_price: float | None = None  # defaults to publication base_price if None
    discount: float = 0.0


class PurchaseOrderUpdate(BaseModel):
    purchase_date: date | None = None
    sale_price: float | None = None
    discount: float | None = None


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_date: date
    customer_id: int
    publication_id: int
    sale_price: float
    discount: float
    customer: CustomerResponse | None = None
    publication: PublicationResponse | None = None
