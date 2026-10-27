from datetime import date
from pydantic import BaseModel, ConfigDict
from backend.schemas.customer import CustomerResponse
from backend.schemas.publication import PublicationResponse


class BillItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    bill_date: date
    publication_id: int
    price: float
    quantity: int
    discount: float
    amount: float
    customer: CustomerResponse | None = None
    publication: PublicationResponse | None = None
