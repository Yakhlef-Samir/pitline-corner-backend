# User repository implementation
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.repositories.base import CRUDBase
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_display_name(
        self, db: AsyncSession, *, display_name: str
    ) -> Optional[User]:
        """Get user by display name"""
        result = await db.execute(
            select(User).where(User.display_name == display_name)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self, db: AsyncSession, *, user_create: UserCreate
    ) -> User:
        """Create user with hashed password"""
        from app.core.security import get_password_hash
        
        user_data = user_create.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        db_obj = User(**user_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user by email and password"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        
        from app.core.security import verify_password
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    async def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.is_superuser


# Create a singleton instance
user = CRUDUser(User)
