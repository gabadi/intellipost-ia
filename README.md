# IntelliPost AI - Development Setup Guide

IntelliPost AI is an intelligent social media posting platform that leverages AI for content generation and optimization. This repository contains both the backend API (Python/FastAPI) and frontend application (TypeScript/SvelteKit) in a monorepo structure.

## Quick Start

### Prerequisites
- **Python 3.11+** with [UV](https://github.com/astral-sh/uv) installed
- **Node.js 18+** with npm
- **Git** with pre-commit hooks support

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd intellipost-ia

# Install all dependencies (monorepo unified approach)
npm run install:all

# Set up pre-commit hooks
npm run prepare
```

### 2. Verify Installation
```bash
# Run unified quality checks
npm run quality

# Test individual components
npm run lint:backend
npm run typecheck:backend
npm run arch-check
npm run lint:frontend

# Test pre-commit hooks
npm run pre-commit
```

## Project Structure

```
intellipost-ia/
├── backend/                    # Python API Backend
│   ├── domain/                # Core business logic
│   ├── infrastructure/        # External services & data access
│   ├── application/           # Use cases & application services
│   └── api/                   # HTTP endpoints & request handling
├── frontend/                  # TypeScript/SvelteKit Frontend
│   └── src/                   # Source code
├── tests/                     # Test files
├── docs/                      # Project documentation
├── package.json              # Monorepo orchestration & scripts
├── pyproject.toml            # Python project configuration
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
└── README.md                 # This file
```

## Development Workflow

### Python Backend Development

#### Quality Tools
- **Ruff**: Fast linting and formatting
- **Pyright**: Static type checking
- **Tach**: Architectural boundary enforcement

#### Commands
```bash
# Unified monorepo commands (recommended)
npm run lint:backend            # Check for issues
npm run format:backend          # Format code
npm run typecheck:backend       # Type checking
npm run arch-check              # Architectural boundaries
npm run quality                 # Run all quality checks

# Direct uvx commands (when needed)
uvx ruff check backend/         # Check for issues
uvx ruff format backend/        # Format code
uvx pyright backend/            # Type checking
uvx tach check backend/         # Architectural boundaries
```

#### Testing
```bash
# Unified monorepo commands
npm run test:backend            # Run tests with coverage
npm run dev:backend             # Start development server

# Direct uv commands (when needed)
uv run pytest                  # Run tests with coverage
uv run pytest --cov=backend --cov-report=html  # Coverage report
```

### Frontend Development

#### Quality Tools
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **dependency-cruiser**: Dependency validation

#### Commands
```bash
# Unified monorepo commands (recommended)
npm run dev:frontend        # Development server
npm run lint:frontend       # Check formatting and lint
npm run format:frontend     # Format code
npm run typecheck:frontend  # Type checking
npm run build:frontend      # Build for production

# Direct workspace commands (when needed)
npm run dev --workspace=frontend
npm run lint --workspace=frontend
npm run build --workspace=frontend
```

## Quality Gates and Pre-commit Hooks

### Automated Quality Checks
Pre-commit hooks automatically run before each commit to ensure code quality:

1. **Python Quality (Backend)**
   - Ruff linting and formatting
   - Pyright type checking
   - Tach architectural boundary validation

2. **Frontend Quality**
   - Prettier formatting
   - ESLint linting
   - Dependency cruiser validation

3. **General Quality**
   - Trailing whitespace removal
   - End-of-file fixing

4. **Accessibility Standards (WCAG 2.1 AA)**
   - Semantic HTML validation
   - ARIA attribute compliance
   - Color contrast checking
   - Keyboard navigation testing
   - YAML/JSON validation
   - Large file detection
   - Private key detection
   - Conventional commit message format

### Manual Quality Validation
```bash
# Run all quality checks without committing
uv run pre-commit run --all-files

# Run specific hooks
uv run pre-commit run ruff-lint
uv run pre-commit run eslint-check
```

## Architecture & Boundaries

### Python Backend Architecture
The backend follows hexagonal architecture principles with enforced boundaries:

- **Domain**: Core business logic (no external dependencies)
- **Infrastructure**: External services, database access (depends on Domain)
- **Application**: Use cases, application services (depends on Domain)
- **API**: HTTP endpoints, request/response handling (depends on Domain, Application)

### Dependency Rules
- Domain layer has no dependencies on other layers
- Infrastructure and Application can depend on Domain
- API layer can depend on Domain and Application
- Violations are caught by Tach during development

## Configuration Files

### Python Configuration (`pyproject.toml`)
- Project metadata and dependencies
- Ruff linting and formatting rules
- Pyright type checking configuration
- Pytest and coverage settings
- Tach architectural boundary rules

### Frontend Configuration
- `package.json`: Dependencies and scripts
- `eslint.config.js`: ESLint rules and plugins
- `.prettierrc`: Prettier formatting configuration
- `.dependency-cruiser.json`: Dependency validation rules
- `tsconfig.json`: TypeScript configuration

### Pre-commit Configuration (`.pre-commit-config.yaml`)
- Quality tool integrations
- Commit message validation
- File format checking

## Troubleshooting

### Common Setup Issues

#### UV Installation Issues
```bash
# Install UV if not available
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

#### Python Virtual Environment Issues
```bash
# Clear virtual environment and reinstall
rm -rf .venv
uv sync --dev
```

#### Frontend Dependency Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Pre-commit Hook Issues
```bash
# Reinstall pre-commit hooks
uv run pre-commit uninstall
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Update hook versions
uv run pre-commit autoupdate
```

### Quality Check Failures

#### Ruff Failures
```bash
# Most issues can be auto-fixed
uv run ruff check --fix backend/

# For format issues
uv run ruff format backend/
```

#### Pyright Type Errors
- Review type annotations in affected files
- Add missing type hints
- Check import statements and module structure

#### Tach Boundary Violations
- Review import statements between layers
- Ensure dependencies follow hexagonal architecture rules
- Refactor code to respect architectural boundaries

#### ESLint/Prettier Issues
```bash
cd frontend

# Auto-fix ESLint issues
npm run lint:fix

# Format with Prettier
npm run format
```

## Agent Coding First Principles

This project follows "Agent Coding First" principles:

1. **Clear, Consistent Structure**: Predictable project layout and naming
2. **Comprehensive Documentation**: Self-documenting code and clear READMEs
3. **Automated Quality Gates**: Preventing low-quality code from entering the codebase
4. **Type Safety**: Strong typing in both Python and TypeScript
5. **Architectural Boundaries**: Clear separation of concerns and dependencies
6. **Test-Driven Development**: Tests alongside implementation

## Getting Help

### Documentation Resources
- [Python Backend Documentation](docs/backend/)
- [Frontend Documentation](docs/frontend/)
- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)

### Quality Tool Documentation
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pyright Documentation](https://github.com/microsoft/pyright)
- [Tach Documentation](https://docs.gauge.sh/)
- [ESLint Documentation](https://eslint.org/docs/)
- [Prettier Documentation](https://prettier.io/docs/)

### Development Support
- Check existing GitHub issues
- Review code comments and docstrings
- Run quality checks for immediate feedback
- Use pre-commit hooks to catch issues early

---

**Last Updated**: June 22, 2025
**Version**: 0.1.0
