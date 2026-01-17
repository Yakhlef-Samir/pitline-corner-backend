from fastapi import APIRouter

from app.api.api_v1.endpoints import health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])

# Direct Sentry test route at api level
@api_router.get("/sentry-test", status_code=500)
async def sentry_test():
    """Temporary route to validate Sentry error capture."""
    raise RuntimeError("Sentry test exception - remove after verification")
