"""Export API endpoints for CSV and PDF."""

import csv
import io
import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Sale

router = APIRouter(prefix="/exports", tags=["Exports"])
logger = logging.getLogger(__name__)


@router.get("/csv")
async def export_csv(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    db: AsyncSession = Depends(get_db),
):
    """Export sales data to CSV."""
    logger.info(
        "Exporting CSV",
        extra={
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "category": category,
            "region": region,
        },
    )

    try:
        query = select(Sale)

        if start_date and end_date:
            query = query.where(
                Sale.order_date >= start_date,
                Sale.order_date <= end_date,
            )
        if category:
            query = query.where(Sale.category == category)
        if region:
            query = query.where(Sale.region == region)

        query = query.order_by(Sale.order_date.desc())

        result = await db.execute(query)
        sales = result.scalars().all()
    except Exception:
        logger.exception("CSV export query failed")
        raise HTTPException(status_code=500, detail="Failed to export CSV data")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "ID",
        "Order Date",
        "Product ID",
        "Product Name",
        "Category",
        "Quantity",
        "Unit Price",
        "Total Amount",
        "Region",
        "Customer Segment",
    ])

    # Write data rows
    for sale in sales:
        writer.writerow([
            sale.id,
            sale.order_date.isoformat(),
            sale.product_id,
            sale.product_name,
            sale.category,
            sale.quantity,
            float(sale.unit_price),
            float(sale.total_amount),
            sale.region or "",
            sale.customer_segment or "",
        ])

    output.seek(0)

    # Generate filename
    filename = f"sales_export_{date.today().isoformat()}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/pdf")
async def export_pdf():
    """Export sales report to PDF."""
    logger.warning("PDF export requested but is not implemented")
    raise HTTPException(status_code=501, detail="PDF export is not implemented yet")
