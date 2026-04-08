"""Health check API endpoints."""

import logging
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.core.cache import get_redis
from app.core.database import get_db
from app.schemas.analytics import HealthCheck

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Basic health check."""
    return HealthCheck(
        status="healthy",
        database="unknown",
        cache="unknown",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health/db", response_model=HealthCheck)
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """Health check with database connection test."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.exception("Database health check failed")
        db_status = f"error: {exc}"

    try:
        redis = await get_redis()
        await redis.ping()
        cache_status = "connected"
    except Exception as exc:
        logger.exception("Redis health check failed")
        cache_status = f"error: {exc}"

    status = "healthy" if db_status == "connected" and cache_status == "connected" else "degraded"

    return HealthCheck(
        status=status,
        database=db_status,
        cache=cache_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
