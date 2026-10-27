from fastapi import APIRouter
from backend.core.deps import CurrentUser, DbSession
from backend.schemas.user import UserCreate, UserUpdate, UserResponse
from backend.services import user_service

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users(db: DbSession, _: CurrentUser):
    return await user_service.list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DbSession, _: CurrentUser):
    return await user_service.get_user(db, user_id)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, db: DbSession, _: CurrentUser):
    return await user_service.create_user(db, data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: DbSession, _: CurrentUser):
    return await user_service.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: DbSession, _: CurrentUser):
    await user_service.delete_user(db, user_id)
