"""Analytics API endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics import AnalyticsService
from app.schemas.analytics import (
    SummaryStats,
    RevenueTrendResponse,
    TopProductsResponse,
    SalesByCategoryResponse,
    RegionalPerformanceResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=SummaryStats)
async def get_summary(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard summary statistics."""
    service = AnalyticsService(db)
    return await service.get_summary_stats(start_date, end_date)


@router.get("/revenue-trend", response_model=RevenueTrendResponse)
async def get_revenue_trend(
    period_type: str = Query("monthly", pattern="^(daily|weekly|monthly|yearly)$"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get revenue trend by time period."""
    service = AnalyticsService(db)
    data = await service.get_revenue_trend(period_type, start_date, end_date)
    return RevenueTrendResponse(data=data, period_type=period_type)


@router.get("/top-products", response_model=TopProductsResponse)
async def get_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get top-selling products by revenue."""
    service = AnalyticsService(db)
    data = await service.get_top_products(limit, start_date, end_date)
    return TopProductsResponse(data=data, limit=limit)


@router.get("/sales-by-category", response_model=SalesByCategoryResponse)
async def get_sales_by_category(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get sales statistics grouped by category."""
    service = AnalyticsService(db)
    data = await service.get_sales_by_category(start_date, end_date)
    return SalesByCategoryResponse(data=data)


@router.get("/regional-performance", response_model=RegionalPerformanceResponse)
async def get_regional_performance(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get sales performance by region."""
    service = AnalyticsService(db)
    data = await service.get_regional_performance(start_date, end_date)
    return RegionalPerformanceResponse(data=data)
