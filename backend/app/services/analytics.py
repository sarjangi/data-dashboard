"""Analytics service with complex SQL queries."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sale
from app.schemas.analytics import (
    SummaryStats,
    RevenueTrendItem,
    ProductStats,
    CategoryStats,
    RegionalStats,
)
from app.core.cache import get_cached, set_cached
from app.core.config import settings


logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics queries and calculations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _build_cache_key(prefix: str, **params: object) -> str:
        """Create a deterministic cache key for analytics queries."""
        parts = [prefix]
        for key, value in sorted(params.items()):
            parts.append(f"{key}={value if value is not None else 'null'}")
        return ":".join(parts)

    async def _get_cached_value(self, key: str):
        """Safely read cached data without failing the request path."""
        try:
            return await get_cached(key)
        except Exception:
            logger.exception("Failed to read analytics cache", extra={"cache_key": key})
            return None

    async def _set_cached_value(self, key: str, value: object, ttl: int) -> None:
        """Safely write cached data without failing the request path."""
        try:
            await set_cached(key, value, ttl)
        except Exception:
            logger.exception("Failed to write analytics cache", extra={"cache_key": key})

    async def get_summary_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> SummaryStats:
        """Get dashboard summary statistics."""
        cache_key = self._build_cache_key(
            "analytics:summary",
            start_date=start_date,
            end_date=end_date,
        )
        cached = await self._get_cached_value(cache_key)
        if cached is not None:
            return SummaryStats(**cached)

        # Build query with optional date filtering
        query = select(
            func.sum(Sale.total_amount).label("total_revenue"),
            func.count(Sale.id).label("total_orders"),
            func.sum(Sale.quantity).label("total_products_sold"),
            func.avg(Sale.total_amount).label("average_order_value"),
        )

        if start_date and end_date:
            query = query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )

        result = await self.db.execute(query)
        row = result.first()

        # Get top category
        top_category_query = (
            select(Sale.category, func.sum(Sale.total_amount).label("revenue"))
            .group_by(Sale.category)
            .order_by(desc("revenue"))
            .limit(1)
        )

        if start_date and end_date:
            top_category_query = top_category_query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )

        top_category_result = await self.db.execute(top_category_query)
        top_category_row = top_category_result.first()

        # Get top region
        top_region_query = (
            select(Sale.region, func.sum(Sale.total_amount).label("revenue"))
            .where(Sale.region.isnot(None))
            .group_by(Sale.region)
            .order_by(desc("revenue"))
            .limit(1)
        )

        if start_date and end_date:
            top_region_query = top_region_query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )

        top_region_result = await self.db.execute(top_region_query)
        top_region_row = top_region_result.first()

        summary = SummaryStats(
            total_revenue=row.total_revenue or Decimal(0),
            total_orders=row.total_orders or 0,
            total_products_sold=row.total_products_sold or 0,
            average_order_value=row.average_order_value or Decimal(0),
            top_category=top_category_row[0] if top_category_row else None,
            top_region=top_region_row[0] if top_region_row else None,
        )
        await self._set_cached_value(
            cache_key,
            summary.model_dump(mode="json"),
            settings.CACHE_TTL_SHORT,
        )
        return summary

    async def get_revenue_trend(
        self,
        period_type: str = "monthly",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[RevenueTrendItem]:
        """Get revenue trend by period (daily, weekly, monthly, yearly)."""
        cache_key = self._build_cache_key(
            "analytics:revenue-trend",
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
        )
        cached = await self._get_cached_value(cache_key)
        if cached is not None:
            return [RevenueTrendItem(**item) for item in cached]

        # Map period types to PostgreSQL date truncation
        period_map = {
            "daily": "day",
            "weekly": "week",
            "monthly": "month",
            "yearly": "year",
        }

        period_trunc = period_map.get(period_type, "month")

        # Build time-series query
        query = (
            select(
                func.date_trunc(period_trunc, Sale.order_date).label("period"),
                func.sum(Sale.total_amount).label("revenue"),
                func.count(Sale.id).label("order_count"),
                func.avg(Sale.total_amount).label("avg_order_value"),
            )
            .group_by("period")
            .order_by("period")
        )

        if start_date and end_date:
            query = query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )
        else:
            # Default to last 12 months
            default_start = date.today() - timedelta(days=365)
            query = query.where(Sale.order_date >= default_start)

        result = await self.db.execute(query)
        rows = result.all()

        items = [
            RevenueTrendItem(
                period=str(row.period.date()) if hasattr(row.period, 'date') else str(row.period),
                revenue=row.revenue,
                order_count=row.order_count,
                avg_order_value=row.avg_order_value,
            )
            for row in rows
        ]
        await self._set_cached_value(
            cache_key,
            [item.model_dump(mode="json") for item in items],
            settings.CACHE_TTL_MEDIUM,
        )
        return items

    async def get_top_products(
        self,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[ProductStats]:
        """Get top-selling products by revenue."""
        cache_key = self._build_cache_key(
            "analytics:top-products",
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )
        cached = await self._get_cached_value(cache_key)
        if cached is not None:
            return [ProductStats(**item) for item in cached]

        query = (
            select(
                Sale.product_id,
                Sale.product_name,
                func.sum(Sale.total_amount).label("total_revenue"),
                func.sum(Sale.quantity).label("total_quantity"),
                func.count(Sale.id).label("order_count"),
                func.avg(Sale.unit_price).label("avg_price"),
            )
            .group_by(Sale.product_id, Sale.product_name)
            .order_by(desc("total_revenue"))
            .limit(limit)
        )

        if start_date and end_date:
            query = query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )

        result = await self.db.execute(query)
        rows = result.all()

        items = [
            ProductStats(
                product_id=row.product_id,
                product_name=row.product_name,
                total_revenue=row.total_revenue,
                total_quantity=row.total_quantity,
                order_count=row.order_count,
                avg_price=row.avg_price,
            )
            for row in rows
        ]
        await self._set_cached_value(
            cache_key,
            [item.model_dump(mode="json") for item in items],
            settings.CACHE_TTL_MEDIUM,
        )
        return items

    async def get_sales_by_category(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[CategoryStats]:
        """Get sales statistics grouped by category."""
        cache_key = self._build_cache_key(
            "analytics:sales-by-category",
            start_date=start_date,
            end_date=end_date,
        )
        cached = await self._get_cached_value(cache_key)
        if cached is not None:
            return [CategoryStats(**item) for item in cached]

        query = (
            select(
                Sale.category,
                func.sum(Sale.total_amount).label("revenue"),
                func.count(Sale.id).label("order_count"),
                func.count(func.distinct(Sale.product_id)).label("product_count"),
                func.avg(Sale.total_amount).label("avg_order_value"),
            )
            .group_by(Sale.category)
            .order_by(desc("revenue"))
        )

        if start_date and end_date:
            query = query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )

        result = await self.db.execute(query)
        rows = result.all()

        # Calculate total revenue for percentages
        total_revenue = sum(row.revenue for row in rows)

        items = [
            CategoryStats(
                category=row.category,
                revenue=row.revenue,
                order_count=row.order_count,
                product_count=row.product_count,
                avg_order_value=row.avg_order_value,
                percentage_of_total=(
                    (row.revenue / total_revenue * 100) if total_revenue > 0 else Decimal(0)
                ),
            )
            for row in rows
        ]
        await self._set_cached_value(
            cache_key,
            [item.model_dump(mode="json") for item in items],
            settings.CACHE_TTL_MEDIUM,
        )
        return items

    async def get_regional_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[RegionalStats]:
        """Get sales performance by region."""
        cache_key = self._build_cache_key(
            "analytics:regional-performance",
            start_date=start_date,
            end_date=end_date,
        )
        cached = await self._get_cached_value(cache_key)
        if cached is not None:
            return [RegionalStats(**item) for item in cached]

        region_summary_query = (
            select(
                Sale.region,
                func.sum(Sale.total_amount).label("revenue"),
                func.count(Sale.id).label("order_count"),
                func.avg(Sale.total_amount).label("avg_order_value"),
            )
            .where(Sale.region.isnot(None))
            .group_by(Sale.region)
        )

        if start_date and end_date:
            region_summary_query = region_summary_query.where(
                and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            )

        product_ranked_query = (
            select(
                Sale.region.label("region"),
                Sale.product_name.label("top_product"),
                func.row_number()
                .over(
                    partition_by=Sale.region,
                    order_by=(
                        func.sum(Sale.total_amount).desc(),
                        Sale.product_name.asc(),
                    ),
                )
                .label("rank"),
            )
            .where(Sale.region.isnot(None))
            .group_by(Sale.region, Sale.product_name)
        )

        category_ranked_query = (
            select(
                Sale.region.label("region"),
                Sale.category.label("top_category"),
                func.row_number()
                .over(
                    partition_by=Sale.region,
                    order_by=(
                        func.sum(Sale.total_amount).desc(),
                        Sale.category.asc(),
                    ),
                )
                .label("rank"),
            )
            .where(Sale.region.isnot(None))
            .group_by(Sale.region, Sale.category)
        )

        if start_date and end_date:
            date_filter = and_(Sale.order_date >= start_date, Sale.order_date <= end_date)
            product_ranked_query = product_ranked_query.where(date_filter)
            category_ranked_query = category_ranked_query.where(date_filter)

        region_summary_subquery = region_summary_query.subquery()
        top_product_subquery = product_ranked_query.subquery()
        top_category_subquery = category_ranked_query.subquery()

        query = (
            select(
                region_summary_subquery.c.region,
                region_summary_subquery.c.revenue,
                region_summary_subquery.c.order_count,
                region_summary_subquery.c.avg_order_value,
                top_product_subquery.c.top_product,
                top_category_subquery.c.top_category,
            )
            .select_from(region_summary_subquery)
            .join(
                top_product_subquery,
                and_(
                    region_summary_subquery.c.region == top_product_subquery.c.region,
                    top_product_subquery.c.rank == 1,
                ),
            )
            .join(
                top_category_subquery,
                and_(
                    region_summary_subquery.c.region == top_category_subquery.c.region,
                    top_category_subquery.c.rank == 1,
                ),
            )
            .order_by(desc(region_summary_subquery.c.revenue))
        )

        result = await self.db.execute(query)
        rows = result.all()

        items = [
            RegionalStats(
                region=row.region,
                revenue=row.revenue,
                order_count=row.order_count,
                avg_order_value=row.avg_order_value,
                top_product=row.top_product,
                top_category=row.top_category,
            )
            for row in rows
        ]
        await self._set_cached_value(
            cache_key,
            [item.model_dump(mode="json") for item in items],
            settings.CACHE_TTL_MEDIUM,
        )
        return items
