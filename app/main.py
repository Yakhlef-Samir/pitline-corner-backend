import logging
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup"""
    try:
        from app.core.database import engine
        from app.models import User
        from sqlalchemy import text

        async with engine.begin() as conn:
            from app.core.database import Base

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
            # Add new columns if they don't exist (for existing tables)
            await conn.execute(text("""
                DO $$
                BEGIN
                    -- Add profile columns if they don't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name='users' AND column_name='first_name') THEN
                        ALTER TABLE users ADD COLUMN first_name VARCHAR(100);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name='users' AND column_name='last_name') THEN
                        ALTER TABLE users ADD COLUMN last_name VARCHAR(100);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name='users' AND column_name='display_name') THEN
                        ALTER TABLE users ADD COLUMN display_name VARCHAR(100);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name='users' AND column_name='country') THEN
                        ALTER TABLE users ADD COLUMN country VARCHAR(50);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name='users' AND column_name='favorite_f1_team') THEN
                        ALTER TABLE users ADD COLUMN favorite_f1_team VARCHAR(50);
                    END IF;
                    
                    -- Create indexes if they don't exist
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                                 WHERE tablename='users' AND indexname='idx_users_display_name') THEN
                        CREATE INDEX idx_users_display_name ON users(display_name);
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                                 WHERE tablename='users' AND indexname='idx_users_favorite_team') THEN
                        CREATE INDEX idx_users_favorite_team ON users(favorite_f1_team);
                    END IF;
                END $$;
            """))
            
    except Exception as e:
        import structlog

        logger = structlog.get_logger()
        logger.error("Failed to create/update tables", error=str(e))

    yield

    # Cleanup (if needed) goes here


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Virtual Pit Wall - Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Additional CORS for development - allow all origins
# TODO: Remove this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
