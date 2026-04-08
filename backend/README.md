# Data Analytics Dashboard - Backend

Python FastAPI backend for the Data Analytics Dashboard with analytics queries, Redis caching, CSV export, and health checks.

## Tech Stack

- **Python 3.11+**
- **FastAPI 0.115** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL 16** - Data warehouse database
- **Redis** - Query result caching
- **Pydantic v2** - Data validation
- **Logging** - Standard library logging with request-path error reporting

## Features

- ✅ Complex SQL analytics queries (time-series, aggregations, grouping, per-region top results)
- ✅ RESTful API with automatic OpenAPI documentation
- ✅ Redis caching for performance
- ✅ Type-safe with Pydantic schemas
- ✅ Async database operations
- ✅ CSV export functionality
- ✅ Basic unit tests for analytics and export behavior

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services (PostgreSQL, Redis, API)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Seed sample data
docker-compose exec backend python -m app.scripts.seed_data

# Stop services
docker-compose down
```

API will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start PostgreSQL and Redis (using Docker)
docker run -d --name analytics-postgres \
  -e POSTGRES_DB=analytics \
  -e POSTGRES_USER=analytics \
  -e POSTGRES_PASSWORD=analytics123 \
  -p 5432:5432 \
  postgres:16-alpine

docker run -d --name analytics-redis \
  -p 6379:6379 \
  redis:7-alpine

# Seed database
python -m app.scripts.seed_data

# Start development server
uvicorn app.main:app --reload
```

If port `8000` is occupied locally, start the API on another port and point the frontend `VITE_API_URL` to that value.

## API Endpoints

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/summary` | Dashboard summary stats |
| GET | `/api/v1/analytics/revenue-trend` | Revenue by time period |
| GET | `/api/v1/analytics/top-products` | Best-selling products |
| GET | `/api/v1/analytics/sales-by-category` | Sales grouped by category |
| GET | `/api/v1/analytics/regional-performance` | Sales by region including top product and top category |

### Exports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/exports/csv` | Export sales data to CSV |
| GET | `/api/v1/exports/pdf` | Returns `501` until PDF export is implemented |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/db` | Health with DB/cache check |

## Example Queries

### Get Summary Statistics
```bash
curl "http://localhost:8000/api/v1/analytics/summary"
```

### Get Monthly Revenue Trend
```bash
curl "http://localhost:8000/api/v1/analytics/revenue-trend?period_type=monthly"
```

### Get Top 5 Products in Date Range
```bash
curl "http://localhost:8000/api/v1/analytics/top-products?limit=5&start_date=2024-01-01&end_date=2024-12-31"
```

### Export to CSV
```bash
curl -o sales.csv "http://localhost:8000/api/v1/exports/csv?start_date=2024-01-01&end_date=2024-12-31"
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── analytics.py  # Analytics endpoints
│   │   ├── exports.py    # Export endpoints
│   │   └── health.py     # Health checks
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings and env parsing
│   │   ├── database.py   # DB connection
│   │   └── cache.py      # Redis cache
│   ├── models/           # SQLAlchemy models
│   │   └── sale.py       # Sales model
│   ├── schemas/          # Pydantic schemas
│   │   └── analytics.py  # Request/response schemas
│   ├── services/         # Business logic
│   │   └── analytics.py  # Analytics service with SQL queries
│   ├── scripts/          # Utility scripts
│   │   └── seed_data.py  # Sample data generator
│   └── main.py           # FastAPI application
├── tests/                # pytest unit tests
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── Dockerfile            # Container image
└── docker-compose.yml    # Multi-container setup
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

Current tests cover core service behavior and the explicit PDF export `501` contract. They are not full integration coverage.

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/
```

## Environment Variables

Key settings in `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://analytics:analytics123@localhost:5432/analytics
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
ALLOW_CORS_CREDENTIALS=true
```

## Deployment

The backend can be deployed to:
- AWS ECS/Fargate
- Azure App Service
- Google Cloud Run
- Render
- Railway

See main project README for deployment instructions.

## License

MIT License
