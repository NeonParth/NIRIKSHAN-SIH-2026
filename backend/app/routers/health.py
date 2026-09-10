from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database.connection import database_connected
from app.database.schemas.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    connected = database_connected()
    if not connected:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )
    return HealthResponse(status="healthy", database="connected")
