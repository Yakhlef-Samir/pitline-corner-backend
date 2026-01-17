from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.crud import create_user, get_user_by_email
from app.schemas.common import ApiResponse
from app.schemas.user import AuthData, UserCreate, UserPublic

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse[AuthData],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    - **password_confirm**: Password confirmation (must match)

    Returns wrapped response with user info and JWT token.
    """
    # Validate password confirmation
    if user_in.password != user_in.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "PASSWORD_MISMATCH",
                    "message": "Les mots de passe ne correspondent pas",
                }
            },
        )

    # Check if user already exists
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "EMAIL_EXISTS",
                    "message": "Cet email est déjà utilisé",
                }
            },
        )

    # Create user
    user = await create_user(db, user_in)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Build response with user info
    auth_data = AuthData(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic.model_validate(user),
    )

    return ApiResponse(data=auth_data)
