# Data Analytics Dashboard

A full-stack analytics dashboard for exploring sales performance by time period, product, category, and region. The stack is a FastAPI backend with PostgreSQL and Redis, plus a React 19 + Vite frontend using Recharts for data visualization.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61dafb?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript)

## Current Scope

- Dashboard summary metrics for revenue, orders, products sold, average order value, top category, and top region
- Revenue trend analytics with daily, weekly, monthly, and yearly grouping
- Top products, sales by category, and regional performance breakdowns
- Redis-backed caching on analytics endpoints with safe cache fallback behavior
- CSV export for filtered sales data
- Explicit `501 Not Implemented` response for PDF export until that feature is built
- Frontend error handling and lightweight dev-only logging
- Component-level code splitting for the heavier dashboard sections to reduce the initial bundle

## Architecture

```
┌─────────────────┐     REST API       ┌──────────────────┐
│   React App     │◄──────────────────►│  FastAPI Server  │
│   (Vite)        │                    │  (Python 3.11)   │
└─────────────────┘                    └────────┬─────────┘
                                                │
                           ┌────────────────────┼────────────────────┐
                           ▼                    ▼                    ▼
                    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                    │ PostgreSQL  │      │    Redis    │      │ APScheduler │
                    │   (Data     │      │   (Cache)   │      │   (Jobs)    │
                    │  Warehouse) │      │             │      │             │
                    └─────────────┘      └─────────────┘      └─────────────┘
```

## Tech Stack

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.115
- **Database**: PostgreSQL 16 with asyncpg
- **ORM**: SQLAlchemy 2.0 async
- **Cache**: Redis 5
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite 7.3
- **Language**: TypeScript 5.x
- **Charts**: Recharts 3.8
- **HTTP Client**: Axios
- **Date Pickers**: react-datepicker
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 22+
- Docker Desktop or local PostgreSQL 16 + Redis 7

### 1. Start Services

```bash
# Using Docker (recommended)
docker run -d \
  --name analytics-postgres \
  -e POSTGRES_DB=analytics \
  -e POSTGRES_USER=analytics \
  -e POSTGRES_PASSWORD=analytics123 \
  -p 5432:5432 \
  postgres:16-alpine

# Start Redis
docker run -d \
  --name analytics-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Seed sample data
python -m app.scripts.seed_data

# Start development server
uvicorn app.main:app --reload --port 8000
```

Backend runs on: http://localhost:8000
API docs: http://localhost:8000/docs

If port `8000` is already in use, start the API on another port and update `frontend/.env` accordingly.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend runs on: http://localhost:5173

## Project Structure

```
data-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Settings, database, cache
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic response models
│   │   ├── scripts/          # Seed utilities
│   │   ├── services/         # Analytics query layer
│   │   └── main.py           # FastAPI app entry
│   ├── tests/                # Unit tests
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/       # Lazy-loaded chart panels
│   │   │   └── ui/           # Shared UI components
│   │   ├── lib/              # API, logging, error helpers
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx           # Dashboard shell
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
└── README.md
```

## API Endpoints

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/summary` | Dashboard summary statistics |
| GET | `/api/v1/analytics/revenue-trend` | Revenue by time period |
| GET | `/api/v1/analytics/top-products` | Best-selling products |
| GET | `/api/v1/analytics/sales-by-category` | Sales grouped by category |
| GET | `/api/v1/analytics/regional-performance` | Sales by region |

### Exports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/exports/csv` | Export filtered sales data to CSV |
| GET | `/api/v1/exports/pdf` | Returns `501` until PDF export is implemented |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/db` | Database connection check |

## Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql+asyncpg://analytics:analytics123@localhost:5432/analytics
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
ALLOW_CORS_CREDENTIALS=true
```

### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000
```

## Validation

```bash
# Backend tests
cd backend
pytest

# Frontend lint
cd ../frontend
npm run lint

# Frontend production build
npm run build
```

## Notes

- The sample data script recreates the `sales` table and reseeds demo records.
- `regional-performance` now includes `top_product` and `top_category` per region.
- The frontend splits `DateRangePicker`, `RevenueTrendChart`, `CategoryChart`, and `TopProductsTable` into lazy chunks.
- The backend is the source of truth for analytics calculations; the frontend converts decimal-like values to numbers where charting libraries require them.

## Data Model

### Sales Data Schema
```sql
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    region VARCHAR(100),
    customer_segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sales_order_date ON sales(order_date);
CREATE INDEX idx_sales_category ON sales(category);
CREATE INDEX idx_sales_region ON sales(region);
```

## Deployment

See [DEPLOY.md](DEPLOY.md) for deployment instructions.

## Sample Analytics Queries

### Revenue Trend (Time-Series)
```sql
SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(total_amount) as revenue,
    COUNT(DISTINCT product_id) as products_sold,
    SUM(quantity) as total_quantity
FROM sales
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;
```

### Top Products
```sql
SELECT 
    product_name,
    SUM(total_amount) as total_revenue,
    SUM(quantity) as total_sold,
    COUNT(*) as order_count
FROM sales
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 10;
```

### Regional Performance
```sql
SELECT 
    region,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(*) as order_count
FROM sales
GROUP BY region
ORDER BY revenue DESC;
```

## License

MIT License - feel free to use this project for learning or as a portfolio piece.

---

Built to demonstrate Python backend, SQL analytics, API design, caching, testing, and frontend performance optimization.
