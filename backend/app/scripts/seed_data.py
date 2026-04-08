"""Seed sample sales data for testing and demonstration."""

import asyncio
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.core.database import Base
from app.models import Sale

# Sample data
PRODUCTS = [
    {"id": 1, "name": "Laptop Pro 15", "category": "Electronics", "price": 1299.99},
    {"id": 2, "name": "Wireless Mouse", "category": "Electronics", "price": 29.99},
    {"id": 3, "name": "Mechanical Keyboard", "category": "Electronics", "price": 89.99},
    {"id": 4, "name": "USB-C Cable", "category": "Accessories", "price": 12.99},
    {"id": 5, "name": "Monitor 27\"", "category": "Electronics", "price": 349.99},
    {"id": 6, "name": "Office Chair", "category": "Furniture", "price": 249.99},
    {"id": 7, "name": "Desk Lamp", "category": "Furniture", "price": 45.99},
    {"id": 8, "name": "Standing Desk", "category": "Furniture", "price": 599.99},
    {"id": 9, "name": "Headphones Pro", "category": "Electronics", "price": 199.99},
    {"id": 10, "name": "Webcam HD", "category": "Electronics", "price": 79.99},
    {"id": 11, "name": "Notebook Set", "category": "Stationery", "price": 15.99},
    {"id": 12, "name": "Pen Premium", "category": "Stationery", "price": 8.99},
    {"id": 13, "name": "Backpack", "category": "Accessories", "price": 59.99},
    {"id": 14, "name": "Phone Stand", "category": "Accessories", "price": 19.99},
    {"id": 15, "name": "Coffee Maker", "category": "Appliances", "price": 89.99},
]

REGIONS = ["North", "South", "East", "West", "Central"]
CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Small Business", "Enterprise"]


async def generate_sales_data(session: AsyncSession, num_records: int = 1000):
    """Generate sample sales data."""
    print(f"Generating {num_records} sales records...")

    # Generate data for the last 2 years
    end_date = date.today()
    start_date = end_date - timedelta(days=730)

    sales = []
    for i in range(num_records):
        product = random.choice(PRODUCTS)
        quantity = random.randint(1, 5)
        unit_price = Decimal(str(product["price"]))
        total_amount = unit_price * quantity

        # Random date within range
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        order_date = start_date + timedelta(days=random_days)

        sale = Sale(
            order_date=order_date,
            product_id=product["id"],
            product_name=product["name"],
            category=product["category"],
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            region=random.choice(REGIONS),
            customer_segment=random.choice(CUSTOMER_SEGMENTS),
        )
        sales.append(sale)

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_records} records...")

    # Bulk insert
    print("Inserting data into database...")
    session.add_all(sales)
    await session.commit()
    print(f"✅ Successfully inserted {num_records} sales records!")


async def main():
    """Main function to seed database."""
    print("Data Analytics Dashboard - Seed Data Script")
    print("=" * 50)

    # Create engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    print("\n1. Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created!")

    # Seed data
    print("\n2. Seeding sample data...")
    async with async_session() as session:
        await generate_sales_data(session, num_records=2000)

    # Close engine
    await engine.dispose()

    print("\n" + "=" * 50)
    print("✅ Database seeding complete!")
    print("\nYou can now start the API server:")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
