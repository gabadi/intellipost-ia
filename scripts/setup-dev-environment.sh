#!/bin/bash
# Setup development environment for User Registration (Story 6.1)

set -e

echo "=== IntelliPost Development Environment Setup ==="
echo ""

# Check if .env file exists
if [ ! -f ../.env ]; then
    echo "❌ .env file not found. Creating from .env.example..."
    cp ../.env.example ../.env
    echo "✅ .env file created. Please update JWT secrets before running the application."
else
    echo "✅ .env file exists"
fi

# Check Docker services
echo ""
echo "Checking Docker services..."
if ! docker compose ps | grep -q "intellipost-ia-postgres-1.*healthy"; then
    echo "Starting PostgreSQL database..."
    docker compose up -d postgres
    echo "Waiting for database to be ready..."
    sleep 5
else
    echo "✅ PostgreSQL is running"
fi

if ! docker compose ps | grep -q "intellipost-ia-minio-1.*Up"; then
    echo "Starting MinIO object storage..."
    docker compose up -d minio
    echo "Waiting for MinIO to be ready..."
    sleep 5
else
    echo "✅ MinIO is running"
fi

# Check Python environment
echo ""
echo "Checking Python environment..."
if [ -d "backend/.venv" ]; then
    echo "✅ Python virtual environment exists"
else
    echo "Creating Python virtual environment..."
    cd backend && uv venv && cd ..
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
cd backend && uv sync && cd ..

# Run database migrations
echo ""
echo "Running database migrations..."
cd backend
source .venv/bin/activate
alembic upgrade head
cd ..

# Create user tables migration if needed
echo ""
echo "Checking for user tables..."
cd backend
source .venv/bin/activate
python -c "
import asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
from infrastructure.config.settings import settings

async def check_tables():
    engine = create_async_engine(settings.get_database_url())
    async with engine.connect() as conn:
        def check(conn):
            inspector = inspect(conn)
            tables = inspector.get_table_names()
            if 'users' in tables:
                print('✅ User table exists')
            else:
                print('❌ User table not found. Run: alembic revision -m \"create user tables\" --autogenerate')
            return tables

        tables = await conn.run_sync(check)
        print(f'Found tables: {tables}')

    await engine.dispose()

asyncio.run(check_tables())
"
cd ..

# Development environment summary
echo ""
echo "=== Development Environment Status ==="
echo ""
echo "1. Database Setup:"
echo "   - PostgreSQL: Running on localhost:5443"
echo "   - Database: intellipost_dev"
echo "   - User: intellipost_user"
echo ""
echo "2. Object Storage:"
echo "   - MinIO: Running on localhost:9002 (API) / localhost:9091 (Console)"
echo "   - Access Key: dev_access_key"
echo "   - Secret Key: dev_secret_key"
echo ""
echo "3. JWT Configuration:"
echo "   - Main Secret Key: Configured in .env (INTELLIPOST_SECRET_KEY)"
echo "   - User JWT Secret: Configured in .env (INTELLIPOST_USER_JWT_SECRET_KEY)"
echo "   - Token Expiry: 30 minutes (configurable)"
echo ""
echo "4. HTTPS/TLS:"
echo "   - Development: HTTP only (localhost:8000)"
echo "   - Production: Configure reverse proxy (nginx/Caddy) with Let's Encrypt"
echo ""
echo "5. Testing Environment:"
echo "   - Test Database: intellipost_test (localhost:5433)"
echo "   - Test Runner: pytest with asyncio support"
echo "   - Coverage: pytest-cov configured"
echo ""
echo "=== Next Steps ==="
echo "1. Update JWT secrets in .env file (if not already done)"
echo "2. Create user table migration: cd backend && alembic revision -m 'create user tables' --autogenerate"
echo "3. Run the migration: alembic upgrade head"
echo "4. Start the backend: cd backend && uvicorn main:app --reload"
echo ""
echo "For production deployment:"
echo "- Set up HTTPS with a reverse proxy (nginx/Caddy)"
echo "- Use environment-specific .env files"
echo "- Enable SSL/TLS termination at the reverse proxy level"
