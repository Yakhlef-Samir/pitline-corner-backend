import logging

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.api.api_v1.api import api_router
from app.core.config import settings


def configure_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


def configure_sentry():
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration(transaction_style="url")],
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=1.0,
            send_default_pii=True,
        )


configure_logging()
configure_sentry()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Virtual Pit Wall - Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        from app.core.database import engine
        from app.models import User

        async with engine.begin() as conn:
            from app.core.database import Base

            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        import structlog

        logger = structlog.get_logger()
        logger.error("Failed to create tables", error=str(e))


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "ok", "message": "Pitline Corner Backend is healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
