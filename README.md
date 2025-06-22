# IntelliPost AI

Intelligent social media posting platform with AI content generation. Monorepo with Python/FastAPI backend and TypeScript/SvelteKit frontend.

## Quick Start

```bash
# Setup
npm run install:all
npm run prepare

# Development
npm run dev                    # Start both frontend and backend
npm run quality               # Run all quality checks
```

## Project Structure

```
intellipost-ia/
├── backend/                  # Python/FastAPI API
│   ├── domain/              # Core business logic
│   ├── infrastructure/      # External services & data
│   ├── application/         # Use cases & services
│   └── api/                 # HTTP endpoints
├── frontend/                # TypeScript/SvelteKit UI
├── tests/                   # Test files
└── docs/                    # Detailed documentation
```

## Essential Commands

### Development
```bash
npm run dev:backend          # FastAPI server (port 8000)
npm run dev:frontend         # SvelteKit dev server
npm run test:backend         # Python tests with coverage
npm run test:frontend        # Frontend tests
```

### Quality & Validation
```bash
npm run ci                   # 🚀 Complete CI pipeline: install + quality + tests
npm run quality              # All quality checks (lint + typecheck + arch)
npm run lint:backend         # Ruff linting
npm run typecheck:backend    # Pyright type checking
npm run arch-check           # Tach boundary validation
npm run lint:frontend        # ESLint + Prettier
npm run test                 # Run all tests (backend + frontend)

# Comprehensive validation (for troubleshooting and setup verification)
./scripts/validate-quality.sh  # 🔍 Complete NFR8.1 validation with detailed output
```

## Architecture

**Backend**: Hexagonal architecture with enforced boundaries
- `domain/`: Core business logic (no external deps)
- `infrastructure/`: External services (depends on domain)
- `application/`: Use cases (depends on domain)
- `api/`: HTTP layer (depends on domain, application)

**Tech Stack**:
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- Frontend: TypeScript, SvelteKit, Node.js 18+
- Quality: Ruff, Pyright, Tach, ESLint, Prettier
- Tools: UV (Python), npm (JS), pre-commit hooks

## Configuration

- `pyproject.toml`: Python config, Ruff, Pyright, Tach rules
- `package.json`: Monorepo scripts and dependencies
- `.pre-commit-config.yaml`: Quality gates

## Key Features

- Hexagonal architecture with boundary enforcement
- Unified monorepo development workflow
- Comprehensive quality gates and type safety
- Agent-friendly codebase structure

---
*Version 0.1.0 | For detailed setup and troubleshooting: see docs/*
