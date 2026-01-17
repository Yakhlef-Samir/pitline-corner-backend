import os
import sys


def test_project_structure():
    """Test that all required directories and files exist"""

    required_dirs = [
        "app",
        "app/api",
        "app/api/api_v1",
        "app/api/api_v1/endpoints",
        "app/core",
        "app/models",
        "app/schemas",
        "app/services",
        "app/utils",
        "alembic",
        "alembic/versions",
        "tests",
    ]

    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/core/redis.py",
        "app/api/api_v1/api.py",
        "app/api/api_v1/endpoints/health.py",
        "alembic.ini",
        "alembic/env.py",
        "alembic/script.py.mako",
        "requirements.txt",
        "README.md",
        ".gitignore",
        ".env.example",
        "pyproject.toml",
        "Dockerfile",
    ]

    print("🔍 Testing project structure...")

    # Test directories
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)

    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ All required directories exist")

    # Test files
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")

    # Test Python imports
    try:
        sys.path.append(".")
        print("🔍 Testing Python imports...")

        # Test main app structure
        with open("app/main.py", "r") as f:
            content = f.read()
            print(f"📄 Main.py content preview: {content[:200]}...")
            if "FastAPI" in content:
                print("✅ FastAPI import found")
            else:
                print("❌ FastAPI import missing")
                return False

            if "uvicorn.run" in content:
                print("✅ uvicorn.run found")
            else:
                print("❌ uvicorn.run missing")
                return False

            print("✅ Main app structure looks correct")

        # Test config structure
        with open("app/core/config.py", "r") as f:
            content = f.read()
            if "BaseSettings" in content and "DATABASE_URL" in content:
                print("✅ Config structure looks correct")
            else:
                print("❌ Config structure issue")
                return False

        print("✅ All Python structure tests passed")
        return True

    except Exception as e:
        print(f"❌ Error testing Python structure: {e}")
        return False


if __name__ == "__main__":
    success = test_project_structure()
    if success:
        print("\n🎉 All structure tests passed!")
        print("📋 Project is ready for FastAPI setup")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
