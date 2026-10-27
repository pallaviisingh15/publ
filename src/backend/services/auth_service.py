from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import create_access_token, verify_password
from backend.db.models.user import User


async def authenticate(db: AsyncSession, username: str, password: str) -> str | None:
    result = await db.execute(select(User).where(User.username == username, User.is_active == True))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return create_access_token(subject=user.id)
