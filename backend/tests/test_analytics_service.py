"""Tests for analytics service behavior."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas.analytics import RegionalStats, SummaryStats
from app.services.analytics import AnalyticsService


class StubResult:
    """Small result stub for mocked SQLAlchemy calls."""

    def __init__(self, *, first_value=None, all_value=None):
        self._first_value = first_value
        self._all_value = all_value or []

    def first(self):
        """Return the first row from a stubbed query."""
        return self._first_value

    def all(self):
        """Return all rows from a stubbed query."""
        return self._all_value


@pytest.mark.asyncio
async def test_get_summary_stats_returns_expected_top_fields():
    """Summary stats should include the derived top category and region."""
    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            StubResult(
                first_value=SimpleNamespace(
                    total_revenue=Decimal("100.00"),
                    total_orders=4,
                    total_products_sold=12,
                    average_order_value=Decimal("25.00"),
                )
            ),
            StubResult(first_value=("Electronics", Decimal("60.00"))),
            StubResult(first_value=("West", Decimal("55.00"))),
        ]
    )

    service = AnalyticsService(db)

    result = await service.get_summary_stats()

    assert result == SummaryStats(
        total_revenue=Decimal("100.00"),
        total_orders=4,
        total_products_sold=12,
        average_order_value=Decimal("25.00"),
        top_category="Electronics",
        top_region="West",
    )


@pytest.mark.asyncio
async def test_get_regional_performance_includes_top_product_and_category():
    """Regional performance should surface top product and category values."""
    db = AsyncMock()
    db.execute = AsyncMock(
        return_value=StubResult(
            all_value=[
                SimpleNamespace(
                    region="West",
                    revenue=Decimal("250.00"),
                    order_count=3,
                    avg_order_value=Decimal("83.33"),
                    top_product="Laptop Pro 15",
                    top_category="Electronics",
                )
            ]
        )
    )

    service = AnalyticsService(db)

    result = await service.get_regional_performance()

    assert result == [
        RegionalStats(
            region="West",
            revenue=Decimal("250.00"),
            order_count=3,
            avg_order_value=Decimal("83.33"),
            top_product="Laptop Pro 15",
            top_category="Electronics",
        )
    ]
