"""
CodeBridge backend entry point.

Run from the `backend/` directory:
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/docs for Swagger UI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.middleware.error_handler import register_error_handlers
from src.routes.api_routes import router as api_router

app = FastAPI(
    title="CodeBridge API",
    description="Translation layer between ICD-11 and NAMASTE/TM2 codes for AYUSH hospitals.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(api_router)


@app.get("/", tags=["health"], summary="Health check")
def health_check():
    return {"status": "ok", "service": "codebridge-api", "env": settings.ENV}