"""Tests for authentication endpoints"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# Test database URL - use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    """Override database dependency for tests"""
    async with TestSessionLocal() as session:
        yield session


# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Set up test database before each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Create async test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()

    # Check response format: { data: { ... }, meta: { ... } }
    assert "data" in data
    assert "meta" in data

    # Check data contents
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert "user" in data["data"]

    # Check user info
    user = data["data"]["user"]
    assert user["email"] == "test@example.com"
    assert user["tier"] == "freemium"
    assert "id" in user

    # Check meta
    assert "timestamp" in data["meta"]


@pytest.mark.asyncio
async def test_register_email_exists(client: AsyncClient):
    """Test registration with existing email returns EMAIL_EXISTS error"""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )

    # Second registration with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password456",
            "password_confirm": "password456",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["error"]["code"] == "EMAIL_EXISTS"


@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient):
    """Test registration with mismatched passwords returns PASSWORD_MISMATCH error"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "password_confirm": "differentpassword",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["error"]["code"] == "PASSWORD_MISMATCH"


@pytest.mark.asyncio
async def test_register_password_too_short(client: AsyncClient):
    """Test registration with short password returns validation error"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "short",
            "password_confirm": "short",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email returns validation error"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "password123",
            "password_confirm": "password123",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_jwt_token_valid(client: AsyncClient):
    """Test that returned JWT token is valid"""
    from jose import jwt

    from app.core.config import settings

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "jwttest@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    token = data["data"]["access_token"]

    # Decode and verify the token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "jwttest@example.com"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_register_user_tier_is_freemium(client: AsyncClient):
    """Test that registered user has freemium tier by default"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tiertest@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["user"]["tier"] == "freemium"
