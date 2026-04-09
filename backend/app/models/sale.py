"""Sales data model."""

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, Index
from sqlalchemy.sql import func

from app.core.database import Base


class Sale(Base):
    """Sales transaction model."""

    __tablename__ = "sales"
    __table_args__ = (
        Index("idx_sales_order_date_category", "order_date", "category"),
        Index("idx_sales_region_category", "region", "category"),
        {"schema": "analytics"},
    )

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(Date, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    region = Column(String(100), index=True)
    customer_segment = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Sale(id={self.id}, product={self.product_name}, amount={self.total_amount})>"
