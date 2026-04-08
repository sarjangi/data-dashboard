# Data Analytics Dashboard - Deployment Guide

This guide covers deploying the Data Analytics Dashboard to production.

## Architecture Overview

```
┌─────────────┐       ┌──────────────┐       ┌────────────┐
│   Vercel    │──────►│  AWS/Azure   │──────►│ PostgreSQL │
│  (Frontend) │       │  (Backend)   │       │   (RDS)    │
└─────────────┘       └──────────────┘       └────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │    Redis     │
                      │   (Cache)    │
                      └──────────────┘
```

## Prerequisites

- [ ] GitHub repository created
- [ ] Vercel account (for frontend)
- [ ] AWS or Azure account (for backend)
- [ ] PostgreSQL database (AWS RDS or Azure Database)
- [ ] Redis instance (AWS ElastiCache or Azure Cache)

## Pre-Deployment Validation

Run the same checks locally that CI runs in `.github/workflows/ci.yml`:

```bash
# Backend
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest

# Frontend
cd ../frontend
npm ci
npm run lint
npm run build
```

---

## Option 1: Deploy to Vercel (Frontend) + Render (Backend)

### Backend Deployment (Render)

1. **Create Render Account**: https://render.com

2. **Create PostgreSQL Database**:
   - Go to Dashboard → New → PostgreSQL
   - Choose plan (Free tier available)
   - Note the connection string

3. **Create Redis Instance**:
   - Go to Dashboard → New → Redis
   - Choose plan (Free tier available)
   - Note the connection string

4. **Deploy Backend**:
   - Go to Dashboard → New → Web Service
   - Connect your GitHub repository
   - Configure:
     - **Build Command**: `cd backend && pip install -r requirements.txt`
     - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       ```
       DATABASE_URL=<your-postgres-connection-string>
       REDIS_URL=<your-redis-connection-string>
       CORS_ORIGINS=https://your-frontend-domain.vercel.app
       LOG_LEVEL=INFO
       ```

5. **Seed Initial Data**:
   ```bash
   # In Render Shell
   python -m app.scripts.seed_data
   ```

6. **Note the Backend URL**: e.g., `https://data-dashboard-api.onrender.com`

### Frontend Deployment (Vercel)

1. **Create Vercel Account**: https://vercel.com

2. **Deploy Frontend**:
   - Import your GitHub repository
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variables:
     ```
     VITE_API_URL=https://data-dashboard-api.onrender.com
     ```

3. **Deploy**: Click "Deploy"

4. **Note the Frontend URL**: e.g., `https://data-dashboard.vercel.app`

5. **Update Backend CORS**:
   - Go back to Render
   - Update `CORS_ORIGINS` to include your Vercel URL

---

## Option 2: Deploy to AWS

### Prerequisites
- AWS CLI installed
- Docker installed
- AWS account with permissions for ECS, RDS, ElastiCache

### Step 1: Create PostgreSQL Database (RDS)

```bash
aws rds create-db-instance \
  --db-instance-identifier data-dashboard-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 16.1 \
  --master-username admin \
  --master-user-password <your-password> \
  --allocated-storage 20 \
  --publicly-accessible
```

### Step 2: Create Redis Cache (ElastiCache)

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id data-dashboard-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

### Step 3: Build and Push Docker Images

```bash
# Backend
cd backend
docker build -t data-dashboard-backend .
docker tag data-dashboard-backend:latest <your-ecr-repo>/data-dashboard-backend:latest
docker push <your-ecr-repo>/data-dashboard-backend:latest

# Frontend
cd ../frontend
docker build -t data-dashboard-frontend .
docker tag data-dashboard-frontend:latest <your-ecr-repo>/data-dashboard-frontend:latest
docker push <your-ecr-repo>/data-dashboard-frontend:latest
```

### Step 4: Create ECS Task Definitions

Create `task-definition.json`:

```json
{
  "family": "data-dashboard",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<your-ecr-repo>/data-dashboard-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "<your-rds-connection-string>"
        },
        {
          "name": "REDIS_URL",
          "value": "<your-redis-connection-string>"
        }
      ]
    },
    {
      "name": "frontend",
      "image": "<your-ecr-repo>/data-dashboard-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

### Step 5: Create ECS Service

```bash
aws ecs create-service \
  --cluster default \
  --service-name data-dashboard \
  --task-definition data-dashboard \
  --desired-count 1 \
  --launch-type FARGATE
```

---

## Option 3: Deploy to Azure

### Step 1: Create Resource Group

```bash
az group create --name data-dashboard-rg --location eastus
```

### Step 2: Create PostgreSQL Database

```bash
az postgres server create \
  --resource-group data-dashboard-rg \
  --name data-dashboard-db \
  --location eastus \
  --admin-user admin \
  --admin-password <your-password> \
  --sku-name B_Gen5_1
```

### Step 3: Create Redis Cache

```bash
az redis create \
  --resource-group data-dashboard-rg \
  --name data-dashboard-cache \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### Step 4: Deploy Backend (App Service)

```bash
cd backend

# Create App Service Plan
az appservice plan create \
  --name data-dashboard-plan \
  --resource-group data-dashboard-rg \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --resource-group data-dashboard-rg \
  --plan data-dashboard-plan \
  --name data-dashboard-api \
  --runtime "PYTHON:3.11"

# Configure deployment
az webapp config appsettings set \
  --resource-group data-dashboard-rg \
  --name data-dashboard-api \
  --settings \
    DATABASE_URL=<your-connection-string> \
    REDIS_URL=<your-redis-connection-string>

# Deploy code
az webapp up --name data-dashboard-api --resource-group data-dashboard-rg
```

### Step 5: Deploy Frontend (Static Web App)

```bash
cd frontend

# Build
npm run build

# Create Static Web App
az staticwebapp create \
  --name data-dashboard \
  --resource-group data-dashboard-rg \
  --source ./dist \
  --location eastus
```

---

## Post-Deployment Checklist

### Backend
- [ ] Health check endpoint working (`/health/db`)
- [ ] API documentation accessible (`/docs`)
- [ ] Database connection successful
- [ ] Redis connection successful
- [ ] Sample data seeded
- [ ] CORS configured for frontend domain
- [ ] Environment variables set correctly

### Frontend
- [ ] All API endpoints reachable
- [ ] Charts loading correctly
- [ ] Date filters working
- [ ] CSV export functional
- [ ] No console errors
- [ ] Mobile responsive

### Security
- [ ] HTTPS enabled
- [ ] Database not publicly accessible
- [ ] Environment variables secure
- [ ] CORS properly configured
- [ ] Rate limiting enabled

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring
- [ ] Set up log aggregation
- [ ] Configure performance monitoring
- [ ] Set up alerts for failures

---

## Troubleshooting

### Backend Issues

**Database connection fails**:
```bash
# Check  connection string
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Test connection
psql $DATABASE_URL
```

**Redis connection fails**:
```bash
# Check connection string
REDIS_URL=redis://host:6379/0

# Test connection
redis-cli -u $REDIS_URL ping
```

### Frontend Issues

**API calls fail**:
- Check VITE_API_URL environment variable
- Verify backend CORS settings
- Check browser console for errors

**Charts not rendering**:
- Check API responses in Network tab
- Verify data format matches TypeScript types
- Check for JavaScript errors

---

## Scaling Considerations

### Database
- Enable connection pooling
- Add read replicas for heavy read workloads
- Implement query caching with Redis
- Set up automated backups

### Backend
- Scale horizontally with multiple instances
- Use load balancer
- Implement Redis session store for multi-instance setups
- Consider serverless for variable load

### Frontend
- Use CDN for static assets
- Enable gzip compression
- Implement lazy loading
- Optimize images and assets

---

## Cost Estimation

### Free Tier Option (Render + Vercel)
- Frontend (Vercel): Free
- Backend (Render): Free (with limitations)
- PostgreSQL (Render): Free (512MB)
- Redis (Render): Free (25MB)
- **Total**: $0/month

### Production Option (AWS)
- RDS PostgreSQL (db.t3.micro): ~$15/month
- ElastiCache Redis (cache.t3.micro): ~$12/month
- ECS Fargate (2 tasks @ 0.25 vCPU, 0.5GB): ~$20/month
- S3 + CloudFront: ~$5/month
- **Total**: ~$52/month

### Enterprise Option (Azure)
- PostgreSQL (Basic): ~$25/month
- Redis Cache (Basic): ~$20/month
- App Service (B1): ~$55/month
- Static Web Apps (Free): $0
- **Total**: ~$100/month

---

## Support

For deployment issues, check:
- README.md for setup instructions
- API documentation at `/docs`
- Backend logs for errors
- Frontend console for client errors
