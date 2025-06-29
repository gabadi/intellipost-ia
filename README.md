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
npm run ci                                             # Complete CI pipeline
npm run quality                                        # All quality checks
npm run lint:backend                                   # Ruff linting
npm run typecheck:backend                              # Pyright type checking
npm run arch-check                                     # Architecture boundary validation
npm run lint:frontend                                  # ESLint + Prettier
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

**Backend**: Protocol-based hexagonal architecture with enforced module boundaries
- `modules/*/domain/`: Core business logic (no external dependencies)
- `modules/*/infrastructure/`: External services adapters
- `modules/*/application/`: Use cases and services
- `modules/*/api/`: HTTP endpoints and schemas
- `infrastructure/`: Shared infrastructure (database, logging, config)
- `di/`: Dependency injection containers (composition root)

**Architecture Documentation**:
- `ARCHITECTURE.md` - Comprehensive architecture guide
- `NEW-MODULE-TEMPLATE.md` - Step-by-step implementation template
- `modules/auth/` - Reference implementation
- `/docs/architecture/` - Detailed guides

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

## 🎯 Key Features for LLMs

- **Modular hexagonal architecture**: Clear separation of concerns
- **Type-safe codebase**: Full TypeScript and Python typing
- **Comprehensive testing**: Unit, integration, and E2E tests
- **Quality gates**: Automated linting, formatting, and architecture validation
- **Development workflow**: Docker-based development with hot reloading
- **API documentation**: Auto-generated OpenAPI/Swagger docs
- **Structured logging**: JSON-formatted logs with correlation IDs

## 🚨 Common Issues

- **Port conflicts**: All services use non-default ports (8080, 4000, 5443, 9002, 9091)
- **Database connection**: Ensure PostgreSQL is running on port 5443
- **Alembic in Docker**: Use the fixed Dockerfile with proper PATH configuration
- **Frontend API calls**: Configure to point to `http://localhost:8080`

---
*Version 0.1.0 | LLM-optimized documentation for IntelliPost AI development*
