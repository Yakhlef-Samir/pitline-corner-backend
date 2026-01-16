from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "ok",
        "message": "Pitline Corner Backend API is running",
        "version": "1.0.0"
    }
