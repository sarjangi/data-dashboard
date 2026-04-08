"""Pydantic schemas for analytics API."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


# Analytics Summary
class SummaryStats(BaseModel):
    """Dashboard summary statistics."""

    total_revenue: Decimal = Field(..., description="Total revenue")
    total_orders: int = Field(..., description="Total number of orders")
    total_products_sold: int = Field(..., description="Total products sold")
    average_order_value: Decimal = Field(..., description="Average order value")
    top_category: Optional[str] = Field(None, description="Best performing category")
    top_region: Optional[str] = Field(None, description="Best performing region")


# Revenue Trend
class RevenueTrendItem(BaseModel):
    """Revenue trend data point."""

    period: str = Field(..., description="Time period (e.g., '2024-01')")
    revenue: Decimal = Field(..., description="Revenue for the period")
    order_count: int = Field(..., description="Number of orders")
    avg_order_value: Decimal = Field(..., description="Average order value")


class RevenueTrendResponse(BaseModel):
    """Revenue trend response."""

    data: List[RevenueTrendItem]
    period_type: str = Field(..., description="Period type: 'daily', 'weekly', 'monthly'")


# Top Products
class ProductStats(BaseModel):
    """Product statistics."""

    product_id: int
    product_name: str
    total_revenue: Decimal
    total_quantity: int
    order_count: int
    avg_price: Decimal


class TopProductsResponse(BaseModel):
    """Top products response."""

    data: List[ProductStats]
    limit: int


# Sales by Category
class CategoryStats(BaseModel):
    """Category statistics."""

    category: str
    revenue: Decimal
    order_count: int
    product_count: int
    avg_order_value: Decimal
    percentage_of_total: Optional[Decimal] = None


class SalesByCategoryResponse(BaseModel):
    """Sales by category response."""

    data: List[CategoryStats]


# Regional Performance
class RegionalStats(BaseModel):
    """Regional performance statistics."""

    region: str
    revenue: Decimal
    order_count: int
    avg_order_value: Decimal
    top_product: Optional[str] = None
    top_category: Optional[str] = None


class RegionalPerformanceResponse(BaseModel):
    """Regional performance response."""

    data: List[RegionalStats]


# Date Range Filter
class DateRangeFilter(BaseModel):
    """Date range filter for queries."""

    start_date: Optional[date] = Field(None, description="Start date (inclusive)")
    end_date: Optional[date] = Field(None, description="End date (inclusive)")
    period_type: Optional[str] = Field("monthly", description="Period: 'daily', 'weekly', 'monthly', 'yearly'")


# Export Request
class ExportRequest(BaseModel):
    """Export data request."""

    export_type: str = Field(..., description="Export type: 'csv' or 'pdf'")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    region: Optional[str] = None


# Health Check
class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    database: str
    cache: str
    timestamp: str
