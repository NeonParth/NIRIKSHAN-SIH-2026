from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers.entities import contractors_router, tenders_router
from app.routers.health import router as health_router
from app.routers.projects import router as projects_router
from app.routers.risks import router as risks_router
from app.utils.errors import http_exception_handler, unhandled_exception_handler

settings = get_settings()

app = FastAPI(
    title="NIRIKSHAN API",
    description=(
        "Evidence-driven risk analysis foundation for MPLADS monitoring. "
        "Assessments identify potential anomalies and risk signals; they do not establish fraud or wrongdoing. "
        "Synthetic demo records are labelled data_source=SYNTHETIC."
    ),
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(health_router)
app.include_router(projects_router, prefix="/api/v1")
app.include_router(risks_router, prefix="/api/v1")
app.include_router(contractors_router, prefix="/api/v1")
app.include_router(tenders_router, prefix="/api/v1")
