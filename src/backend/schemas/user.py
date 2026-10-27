from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    username: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    is_active: bool
    created_at: datetime
