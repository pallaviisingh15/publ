from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    name: str
    address: str
    pin: str
    contact_number: str


class CustomerUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    pin: str | None = None
    contact_number: str | None = None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    pin: str
    contact_number: str
