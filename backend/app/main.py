#!/usr/bin/env python3
"""AI Cloud Manager — main entry point."""
import sys, os, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.utils.logging import setup_logging
from app.api.routes import router as api_router

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Cloud Manager",
    version="1.0.0",
    description="Enterprise multi-cloud AI management platform with cost optimization, security scoring, and AI recommendations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

@app.on_event("startup")
async def startup():
    logger.info("AI Cloud Manager starting on %s:%s", settings.host, settings.port)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
