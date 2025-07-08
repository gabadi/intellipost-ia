# IntelliPost AI

Intelligent social media posting platform with AI content generation. Monorepo with Python/FastAPI backend and TypeScript/SvelteKit frontend.

## 🚀 Quick Start

### Docker Development (Recommended)
```bash
# Complete setup with all services
docker compose up -d postgres minio                    # Infrastructure services
docker compose --profile migration run --rm migrations # Run database migrations
docker compose up backend frontend                     # Start application (with logs)

# Or background mode
docker compose up -d backend frontend
```

### Manual Development
```bash
# Setup
npm run install:all
npm run prepare

# Start services
cd backend && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8080
cd frontend && npx vite dev --port 4000
```

## 🌐 Services & Ports

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **Backend API** | 8080 | `http://localhost:8080` | FastAPI server |
| **Frontend** | 4000 | `http://localhost:4000` | SvelteKit app |
| **PostgreSQL** | 5443 | `localhost:5443` | Database |
| **MinIO API** | 9002 | `http://localhost:9002` | S3-compatible storage |
| **MinIO Console** | 9091 | `http://localhost:9091` | Storage management UI |

### Key Endpoints
- API Docs: `http://localhost:8080/docs`
- Health Check: `http://localhost:8080/health`
- API Root: `http://localhost:8080/`

### Default Admin Credentials
After running database migrations, a default admin user is created:
- **Email**: `admin@intellipost.ai`
- **Password**: `admin123`
- **Access**: Full system administration

⚠️ **Security Note**: Change these credentials immediately in production environments!

## 📁 Project Structure

```
intellipost-ia/
├── backend/                  # Python/FastAPI API
│   ├── modules/             # Feature modules (hexagonal architecture)
│   │   ├── auth/           # Authentication module
│   │   ├── product/        # Product management
│   │   ├── ai_content/     # AI content generation
│   │   └── mercadolibre/   # MercadoLibre integration
│   ├── infrastructure/     # External services & config
│   ├── api/                # HTTP endpoints & schemas
│   └── migrations/         # Database migrations
├── frontend/               # TypeScript/SvelteKit UI
│   ├── src/lib/           # Shared components & utils
│   ├── src/routes/        # Page routes
│   └── tests/             # Frontend tests
├── tests/                 # Backend tests
└── docs/                  # Documentation
```

## 🛠️ Essential Commands

### Development
```bash
# Docker (recommended)
docker compose up -d                                   # All services in background
docker compose logs -f backend                         # Follow backend logs
docker compose logs -f frontend                        # Follow frontend logs

# Manual
npm run dev:backend                                    # FastAPI (port 8080)
npm run dev:frontend                                   # SvelteKit (port 4000)

# Testing
npm run test:backend                                   # Python tests with coverage
npm run test:frontend                                  # Frontend tests
cd frontend && npx playwright test                     # E2E tests
```

### Quality & Validation
```bash
# Quality Checks
npm run ci                                             # Complete CI pipeline
npm run quality                                        # All quality checks
npm run lint:backend                                   # Ruff linting
npm run typecheck:backend                              # Pyright type checking
npm run arch-check                                     # Architecture boundary validation
npm run lint:frontend                                  # ESLint + Prettier

# Auto-fix Code Quality Issues (NEVER fix manually!)
cd backend && uvx ruff check --fix .                   # Fix linting issues automatically
cd backend && uvx ruff format .                        # Format code automatically
cd frontend && npm run lint:fix                        # Fix frontend linting & formatting

# Test Categorization Enforcement
cd backend && uv run pytest -m unit                    # Run only unit tests (178 tests)
cd backend && uv run pytest -m integration             # Run only integration tests (77 tests)
# ⚠️ All tests MUST have @pytest.mark.unit or @pytest.mark.integration marks
# ⚠️ Tests without marks will cause CI to fail immediately
```

### Database Operations
```bash
# Migrations
docker compose --profile migration run --rm migrations # Run all migrations
cd backend && uv run alembic upgrade head              # Manual migration
cd backend && uv run alembic revision --autogenerate -m "description" # Create migration

# Database access
docker exec -it intellipost-ia-postgres-1 psql -U intellipost_user -d intellipost_dev
```

## 🏗️ Architecture

**Backend**: Hexagonal architecture with enforced module boundaries
- `modules/*/domain/`: Core business logic (no external dependencies)
- `modules/*/infrastructure/`: External services adapters
- `modules/*/application/`: Use cases and services
- `modules/*/api/`: HTTP endpoints and schemas
- `infrastructure/`: Shared infrastructure (database, logging, config)

**Tech Stack**:
- **Backend**: Python 3.13+, FastAPI, SQLAlchemy, Pydantic, Alembic
- **Frontend**: TypeScript, SvelteKit, Vite, Playwright
- **Database**: PostgreSQL 15+
- **Storage**: MinIO (S3-compatible)
- **Quality**: Ruff, Pyright, Tach, ESLint, Prettier
- **Tools**: UV (Python), npm (JS), Docker, pre-commit hooks

## 🔧 Configuration Files

- `docker-compose.yml`: Service orchestration with custom ports
- `backend/pyproject.toml`: Python dependencies and tool configuration
- `frontend/package.json`: Frontend dependencies and scripts
- `backend/infrastructure/config/settings.py`: Application configuration
- `.pre-commit-config.yaml`: Quality gates and hooks

### Environment Configuration

The application uses hierarchical environment configuration:
- **Development**: Backend runs on port 8000, exposed via Docker on 8080
- **Frontend**: Connects to backend via `VITE_API_BASE_URL` (defaults to localhost:8000)
- **Testing**: Uses `.env.testing` with consistent port configuration for CI/CD

## 🎯 Key Features for LLMs

- **Modular hexagonal architecture**: Clear separation of concerns
- **Type-safe codebase**: Full TypeScript and Python typing
- **Comprehensive testing**: Unit, integration, and E2E tests
- **Quality gates**: Automated linting, formatting, and architecture validation
- **Development workflow**: Docker-based development with hot reloading
- **API documentation**: Auto-generated OpenAPI/Swagger docs
- **Structured logging**: JSON-formatted logs with correlation IDs

## 🔄 Development Workflow

### Before Committing Changes
Always run the complete CI pipeline locally to ensure your changes pass all checks:

```bash
# 1. Fix any code quality issues automatically
cd backend && uvx ruff check --fix .
cd backend && uvx ruff format .

# 2. Run all quality checks
cd backend && uvx ruff check .                         # Should show "All checks passed!"
cd backend && uv run pyright                           # Should show "0 errors, 0 warnings"
cd backend && uvx tach check                           # Should show "✅ All modules validated!"
cd backend && uvx bandit -r modules/ infrastructure/ api/ --exclude='*/tests/*,*/test_*.py,*/fixtures/*' --skip=B101,B601,B105,B106,B110

# 3. Run tests
cd backend && uv run pytest -m unit -q                 # Should pass 178 unit tests
cd backend && uv run pytest -m integration -q          # Should recognize 77 integration tests

# 4. Only commit if ALL checks pass
git add . && git commit -m "your message"
```

### Code Quality Standards
- **Formatting**: Use `uvx ruff format .` - NEVER format manually
- **Linting**: Use `uvx ruff check --fix .` - NEVER fix linting issues manually
- **Test Marks**: ALL tests MUST have `pytestmark = pytest.mark.unit` or `pytestmark = pytest.mark.integration`
- **Type Safety**: All code must pass Pyright type checking
- **Architecture**: Module boundaries enforced by Tach

## 🚨 Common Issues & Solutions

### Port Configuration
- **Development**: Backend runs on port 8000, accessible at `http://localhost:8000`
- **Docker**: Backend exposed on port 8080, internally running on 8000
- **Frontend**: Always configure to point to `http://localhost:8080` for Docker or `http://localhost:8000` for direct development

### Environment Issues
- **CI/CD Testing**: Uses `.env.testing` file for consistent test configuration
- **Database connection**: Ensure PostgreSQL is running on port 5443 (development) or 5432 (CI)
- **API connectivity**: Check that `INTELLIPOST_API_PORT` matches your environment

### Docker Issues
- **Alembic in Docker**: Use the fixed Dockerfile with proper PATH configuration
- **Port conflicts**: All services use non-default ports (8080, 4000, 5443, 9002, 9091)
- **Environment variables**: Ensure Docker Compose loads the correct environment settings

---
*Version 0.1.0 | LLM-optimized documentation for IntelliPost AI development*
