# IntelliPost AI - Deployment Strategy

## Document Information
- **Project:** IntelliPost AI MVP
- **Architect:** Winston (Fred)
- **Date:** June 22, 2025
- **Focus:** Docker Compose MVP → Production Scalability
- **Philosophy:** Start simple, scale progressively

---

## Deployment Architecture Overview

### MVP Philosophy: Docker Compose First
```yaml
MVP Strategy:
  - Single docker-compose.yml for all environments
  - Consistent development → staging → production
  - Minimal infrastructure complexity
  - Easy debugging and rapid iteration

Post-MVP Scaling:
  - Kubernetes when needed (100+ concurrent users)
  - Managed services when justified
  - Cost-driven decisions, not tech-driven
```

---

## 1. Docker Compose Architecture

### Complete Stack Definition
```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI Backend
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: intellipost-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/intellipost
      - STORAGE_URL=http://storage:9000
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PHOTOROOM_API_KEY=${PHOTOROOM_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=${ENVIRONMENT:-development}
    depends_on:
      - db
      - storage
    volumes:
      - ./backend:/app
      - /app/__pycache__
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - intellipost-network
    restart: unless-stopped

  # SvelteKit Frontend
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: intellipost-web
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://api:8000
      - PUBLIC_API_URL=${PUBLIC_API_URL:-http://localhost:8000}
    depends_on:
      - api
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
    networks:
      - intellipost-network
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: intellipost-db
    environment:
      - POSTGRES_DB=intellipost
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - intellipost-network
    restart: unless-stopped

  # MinIO Object Storage (S3-compatible)
  storage:
    image: minio/minio:latest
    container_name: intellipost-storage
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    networks:
      - intellipost-network
    restart: unless-stopped

  # Redis (Future - for WebSocket scaling)
  # redis:
  #   image: redis:7-alpine
  #   container_name: intellipost-redis
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   networks:
  #     - intellipost-network
  #   restart: unless-stopped

  # Nginx Reverse Proxy
  proxy:
    image: nginx:alpine
    container_name: intellipost-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
      - web
    networks:
      - intellipost-network
    restart: unless-stopped

volumes:
  postgres_data:
  minio_data:
  # redis_data:

networks:
  intellipost-network:
    driver: bridge
```

### Environment Configuration
```bash
# .env.development
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/intellipost
GEMINI_API_KEY=your_gemini_key_here
PHOTOROOM_API_KEY=your_photoroom_key_here
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
JWT_SECRET=your-super-secret-jwt-key
PUBLIC_API_URL=http://localhost:8000

# .env.production
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:secure_password@db:5432/intellipost
GEMINI_API_KEY=prod_gemini_key
PHOTOROOM_API_KEY=prod_photoroom_key
AWS_ACCESS_KEY_ID=prod_aws_key
AWS_SECRET_ACCESS_KEY=prod_aws_secret
JWT_SECRET=super-secure-production-jwt-secret
PUBLIC_API_URL=https://api.intellipost.ai
```

---

## 2. Backend Dockerfile

### Multi-stage Python Build
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production
COPY . .
RUN pip install --no-cache-dir gunicorn

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Python Dependencies
```text
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.13.0
asyncpg==0.29.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
google-generativeai==0.3.2
boto3==1.34.0
pillow==10.1.0
pytest==7.4.3
pytest-asyncio==0.21.1

# backend/requirements-dev.txt
black==23.11.0
ruff==0.1.6
pyright==1.1.338
pytest-cov==4.1.0
pytest-mock==3.12.0
```

---

## 3. Frontend Dockerfile

### Node.js Multi-stage Build
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine as base

# Install dependencies only when needed
FROM base as deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM base as development
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM base as builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM base as production
WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 sveltekit

# Copy built application
COPY --from=builder --chown=sveltekit:nodejs /app/build ./build
COPY --from=builder --chown=sveltekit:nodejs /app/package.json ./package.json
COPY --from=deps --chown=sveltekit:nodejs /app/node_modules ./node_modules

USER sveltekit

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "build"]
```

---

## 4. Nginx Configuration

### Reverse Proxy Setup
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream web {
        server web:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;

    # Main server block
    server {
        listen 80;
        listen 443 ssl http2;
        server_name intellipost.ai www.intellipost.ai;

        # SSL Configuration (for production)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Frontend routes
        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # CORS headers
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
        }

        # WebSocket routes
        location /ws/ {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # File upload routes (higher limits)
        location /api/v1/products {
            limit_req zone=upload burst=5 nodelay;

            client_max_body_size 50M;
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 5. Database Initialization

### Database Setup Scripts
```sql
-- database/init/01-init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create application database
\c intellipost;

-- Create application user
CREATE USER intellipost_app WITH PASSWORD 'app_password';
GRANT ALL PRIVILEGES ON DATABASE intellipost TO intellipost_app;
GRANT ALL ON SCHEMA public TO intellipost_app;

-- Performance optimizations
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';
```

### Alembic Migration Setup
```python
# backend/alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from src.models import Base
from src.core.config import settings

# Import all models to ensure they're registered
from src.models.user import User
from src.models.product import Product, ProductImage, GeneratedContent
from src.models.ml_credentials import MLCredentials

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = context.config
    configuration.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    connectable = engine_from_config(
        configuration.get_section(configuration.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

---

## 6. Development Workflow

### Local Development Setup
```bash
#!/bin/bash
# scripts/dev-setup.sh

echo "Setting up IntelliPost AI development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose required but not installed."; exit 1; }

# Copy environment file
cp .env.example .env.development

echo "Please edit .env.development with your API keys:"
echo "- GEMINI_API_KEY"
echo "- PHOTOROOM_API_KEY"
read -p "Press enter when ready..."

# Start services
docker-compose --env-file .env.development up -d db storage

# Wait for database
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
docker-compose --env-file .env.development run --rm api alembic upgrade head

# Start all services
docker-compose --env-file .env.development up

echo "Development environment ready!"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "MinIO Console: http://localhost:9001"
```

### Quality Checks Script
```bash
#!/bin/bash
# scripts/quality-check.sh

echo "Running quality checks..."

# Backend checks
echo "Checking backend code quality..."
cd backend

# Type checking
echo "Running Pyright..."
pyright src/

# Linting
echo "Running Ruff..."
ruff check src/

# Code formatting
echo "Running Black..."
black --check src/

# Tests
echo "Running pytest..."
pytest tests/ -v --cov=src --cov-report=term-missing

cd ..

# Frontend checks
echo "Checking frontend code quality..."
cd frontend

# Type checking
echo "Running TypeScript check..."
npm run check

# Linting
echo "Running ESLint..."
npm run lint

# Tests
echo "Running Jest..."
npm run test

cd ..

echo "Quality checks complete!"
```

---

## 7. Production Deployment

### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      target: production
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PHOTOROOM_API_KEY=${PHOTOROOM_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=production
    depends_on:
      - db
    networks:
      - intellipost-network
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  web:
    build:
      context: ./frontend
      target: production
    environment:
      - API_URL=http://api:8000
      - PUBLIC_API_URL=https://api.intellipost.ai
    depends_on:
      - api
    networks:
      - intellipost-network
    restart: unless-stopped
    deploy:
      replicas: 2

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - intellipost-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
      - web
    networks:
      - intellipost-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  intellipost-network:
    driver: bridge
```

### Deployment Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "Deploying IntelliPost AI to production..."

# Backup database
echo "Creating database backup..."
docker-compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql

# Pull latest code
git pull origin main

# Build new images
echo "Building production images..."
docker-compose -f docker-compose.prod.yml build

# Run migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Deploy with zero downtime
echo "Deploying with rolling update..."
docker-compose -f docker-compose.prod.yml up -d --scale api=2 --scale web=2

# Health check
echo "Waiting for services to be healthy..."
sleep 30

# Verify deployment
curl -f https://api.intellipost.ai/health || {
    echo "Deployment failed! Rolling back..."
    docker-compose -f docker-compose.prod.yml rollback
    exit 1
}

echo "Deployment successful!"
```

---

## 8. Monitoring & Health Checks

### Health Check Endpoints
```python
# backend/src/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.ai_service import AIContentGenerator
from src.services.image_service import ImageProcessor

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.now()}

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(),
        "checks": {}
    }

    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # External services check (optional)
    # Could add Gemini/PhotoRoom API checks here

    return health_status
```

### Docker Health Checks
```dockerfile
# Add to backend Dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Add to frontend Dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1
```

---

## 9. Performance Considerations

### Resource Allocation
```yaml
# Production resource limits
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  db:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Scaling Strategy
```yaml
MVP Scale (100-500 concurrent users):
  - 2 API replicas
  - 2 Web replicas
  - Single DB instance
  - Nginx load balancing

Growth Scale (500-2000 users):
  - 4 API replicas
  - 3 Web replicas
  - DB with read replicas
  - Redis for WebSocket scaling
  - CDN for static assets

Enterprise Scale (2000+ users):
  - Kubernetes migration
  - Managed database (RDS)
  - Managed storage (S3)
  - Auto-scaling policies
```

---

## 10. Backup & Disaster Recovery

### Automated Backup Strategy
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec db pg_dump -U postgres intellipost | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# MinIO data backup
docker run --rm -v minio_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/minio_$DATE.tar.gz /data

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Disaster Recovery Plan
```yaml
Recovery Procedures:
  1. Database Restore:
     - Stop all services
     - Restore from latest backup
     - Run migrations if needed
     - Restart services

  2. Complete System Restore:
     - Deploy from git main branch
     - Restore database backup
     - Restore MinIO data
     - Update environment variables
     - Health check verification

RTO Target: 30 minutes
RPO Target: 1 hour (backup frequency)
```

---

**Esta estrategia de deployment completa proporciona una base sólida para MVP con path claro hacia escalabilidad. ¿Algún aspecto específico del deployment que quieras que ajuste o profundice?**
