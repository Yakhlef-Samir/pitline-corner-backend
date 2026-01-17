#!/usr/bin/env python3
"""
Basic test to verify FastAPI app can be created and configured correctly
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_app_creation():
    """Test that we can create a basic FastAPI app without external dependencies"""

    print("🚀 Testing basic FastAPI app creation...")

    try:
        # Test 1: Import FastAPI
        from fastapi import FastAPI

        print("✅ FastAPI import successful")

        # Test 2: Create basic app
        app = FastAPI(title="Test App", version="1.0.0")
        print("✅ FastAPI app creation successful")

        # Test 3: Add basic endpoint
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test working"}

        print("✅ Basic endpoint creation successful")

        # Test 4: Test our app structure
        print("🔍 Testing our app structure...")

        # Test config import
        try:
            from app.core.config import settings

            print("✅ Settings import successful")
            print(f"📋 Project name: {settings.PROJECT_NAME}")
            print(f"📋 API version: {settings.VERSION}")
            print(f"📋 API V1 STR: {settings.API_V1_STR}")
        except Exception as e:
            print(f"❌ Settings import failed: {e}")
            return False

        # Test main app import (without database/redis dependencies)
        try:
            # Mock the database and redis to avoid dependency issues
            import unittest.mock

            with (
                unittest.mock.patch("app.core.database.engine"),
                unittest.mock.patch("app.core.redis.redis_client"),
            ):

                from app.main import app as main_app

                print("✅ Main app import successful")

                # Test that the health endpoint exists
                for route in main_app.routes:
                    if hasattr(route, "path") and route.path == "/health":
                        print("✅ Health endpoint found")
                        break
                else:
                    print("❌ Health endpoint not found")
                    return False

        except Exception as e:
            print(f"❌ Main app import failed: {e}")
            return False

        print("🎉 All basic app tests passed!")
        return True

    except Exception as e:
        print(f"❌ Basic app test failed: {e}")
        return False


def test_acceptance_criteria():
    """Test that acceptance criteria are met"""

    print("\n📋 Testing Acceptance Criteria...")

    # AC1: FastAPI 0.100+ with Python 3.11+
    try:
        import fastapi

        print(f"✅ FastAPI version: {fastapi.__version__}")
        if fastapi.__version__ >= "0.100.0":
            print("✅ FastAPI version meets requirement (>= 0.100.0)")
        else:
            print("❌ FastAPI version too old")
            return False
    except ImportError:
        print("❌ FastAPI not available")
        return False

    import sys

    python_version = sys.version_info
    print(
        f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
    )
    if python_version >= (3, 11):
        print("✅ Python version meets requirement (>= 3.11)")
    else:
        print("❌ Python version too old")
        return False

    # AC2: SQLAlchemy 2.0+ configured (structure exists)
    if os.path.exists("app/core/database.py"):
        print("✅ SQLAlchemy database configuration exists")
    else:
        print("❌ SQLAlchemy database configuration missing")
        return False

    # AC3: PostgreSQL connection configured
    try:
        from app.core.config import settings

        if "postgresql" in str(settings.DATABASE_URL):
            print("✅ PostgreSQL connection configured")
        else:
            print("❌ PostgreSQL connection not configured")
            return False
    except Exception as e:
        print(f"❌ Database configuration test failed: {e}")
        return False

    # AC4: Redis configured for cache
    if os.path.exists("app/core/redis.py"):
        print("✅ Redis configuration exists")
    else:
        print("❌ Redis configuration missing")
        return False

    # AC5: Alembic for migrations
    if os.path.exists("alembic.ini") and os.path.exists("alembic/env.py"):
        print("✅ Alembic migrations configured")
    else:
        print("❌ Alembic migrations not configured")
        return False

    # AC6: Structure according to architecture.md
    required_structure = [
        "app/api",
        "app/core",
        "app/models",
        "app/schemas",
        "app/services",
        "app/utils",
    ]
    for struct in required_structure:
        if os.path.exists(struct):
            print(f"✅ {struct} exists")
        else:
            print(f"❌ {struct} missing")
            return False

    # AC7: Health endpoint exists
    try:
        with open("app/main.py", "r") as f:
            content = f.read()
            if '@app.get("/health")' in content:
                print("✅ Health endpoint exists")
            else:
                print("❌ Health endpoint missing")
                return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

    # AC8: OpenAPI docs endpoint
    try:
        with open("app/main.py", "r") as f:
            content = f.read()
            if "openapi_url" in content:
                print("✅ OpenAPI docs configured")
            else:
                print("❌ OpenAPI docs not configured")
                return False
    except Exception as e:
        print(f"❌ OpenAPI docs test failed: {e}")
        return False

    print("🎉 All Acceptance Criteria tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🏁 Pitline Corner Backend - Setup Verification")
    print("=" * 60)

    success1 = test_basic_app_creation()
    success2 = test_acceptance_criteria()

    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("📋 Backend project is ready for development!")
        print("\n🚀 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Setup PostgreSQL database")
        print("   3. Setup Redis")
        print("   4. Run: uvicorn app.main:app --reload")
        print("   5. Visit: http://localhost:8000/docs")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
