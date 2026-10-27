from pydantic import BaseModel, ConfigDict
from backend.db.models.publication import FrequencyEnum


class PublicationCreate(BaseModel):
    name: str
    frequency: FrequencyEnum
    base_price: float
    purchase_price: float


class PublicationUpdate(BaseModel):
    name: str | None = None
    frequency: FrequencyEnum | None = None
    base_price: float | None = None
    purchase_price: float | None = None


class PublicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    frequency: FrequencyEnum
    base_price: float
    purchase_price: float
