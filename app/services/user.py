# Business logic services
from typing import Optional

from app.repositories.user import user
from app.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    """Service layer for user business logic"""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> Optional[dict]:
        """Create a new user with business logic validation"""
        # Check if user already exists
        existing_user = await user.get_by_email(db, email=user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user
        new_user = await user.create_user(db, user_create=user_data)
        return {
            "id": new_user.id,
            "email": new_user.email,
            "display_name": new_user.display_name,
            "is_active": new_user.is_active,
        }

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[dict]:
        """Authenticate user and return user data"""
        user_obj = await user.authenticate(db, email=email, password=password)
        if not user_obj:
            return None

        if not await user.is_active(user_obj):
            return None

        return {
            "id": user_obj.id,
            "email": user_obj.email,
            "display_name": user_obj.display_name,
            "is_active": user_obj.is_active,
            "is_superuser": user_obj.is_superuser,
        }


# Create service instance
user_service = UserService()
