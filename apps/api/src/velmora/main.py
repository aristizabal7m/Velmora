import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from velmora.api.v1.router import router as api_router
from velmora.core.config import settings
from velmora.core.errors import register_exception_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("velmora")

app = FastAPI(
    title="VELMORA API",
    description="API educativa para explorar alternativas de inversión en Colombia.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["sistema"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment, "version": "0.1.0"}
