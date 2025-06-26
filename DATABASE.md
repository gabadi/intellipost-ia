# Database Migration Strategy

## Overview

The IntelliPost AI backend uses **Alembic** for database migrations with PostgreSQL. This document explains where and how migrations are executed.

## Migration Execution Points

### 1. Development Environment (docker-compose.yml)

**Current Strategy**: Migrations run automatically with backend startup
```bash
# Backend service command
sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
```

**Alternative Strategy**: Separate migration service
```bash
# Run migrations separately
docker compose --profile migration up migrations

# Then start normal services
docker compose up backend frontend
```

### 2. Production Environment

**Recommended Approach**: Run migrations as separate deployment step
```bash
# During deployment, before starting new backend instances
alembic upgrade head
```

**Benefits**:
- ✅ Fail-fast if migrations fail
- ✅ Better control over deployment process
- ✅ Clear separation of concerns
- ✅ Easier to troubleshoot migration issues

### 3. CI/CD Pipeline

**Integration Points**:
1. **Test Stage**: Run migrations on test database
2. **Staging Stage**: Run migrations on staging database
3. **Production Stage**: Run migrations before deploying new code

## Migration Files Location

```
backend/
├── alembic.ini           # Alembic configuration
├── migrations/           # Migration scripts directory
│   ├── env.py           # Migration environment setup
│   ├── script.py.mako   # Migration template
│   └── versions/        # Individual migration files
└── infrastructure/
    └── database/        # Database models and setup
```

## Migration Configuration

### Environment Variables
- `INTELLIPOST_DATABASE_URL`: Database connection string
- `INTELLIPOST_ENVIRONMENT`: Environment (development/production/testing)

### Automatic Configuration
The migration environment (`migrations/env.py`) automatically:
- Loads settings from `infrastructure.config.settings`
- Configures database URL based on environment
- Supports async database operations
- Includes all model metadata for autogeneration

## Running Migrations

### Development
```bash
# Automatic (with docker-compose)
docker compose up

# Manual
cd backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add user table"
```

### Production
```bash
# In production container/environment
alembic upgrade head

# Or in CI/CD pipeline
docker run --env-file .env.prod backend-image alembic upgrade head
```

### Testing
```bash
# Test database uses separate URL
INTELLIPOST_ENVIRONMENT=testing alembic upgrade head
```

## Migration Best Practices

### 1. Safe Migration Strategies
- **Backward Compatible**: Ensure migrations can coexist with old code versions
- **Rollback Support**: Always test rollback procedures
- **Data Preservation**: Never delete data in migrations without backups

### 2. Performance Considerations
- **Large Tables**: Use partitioned operations for large datasets
- **Indexes**: Create indexes concurrently in production
- **Locks**: Minimize table locks during migrations

### 3. Testing
- **Local Testing**: Test migrations against copy of production data
- **Staging Environment**: Always test in staging before production
- **Rollback Testing**: Test rollback procedures regularly

## Docker Compose Migration Options

### Option 1: Integrated (Current)
**Pros**: Simple, automatic
**Cons**: Backend fails if migrations fail
```yaml
backend:
  command: sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
```

### Option 2: Separate Service
**Pros**: Better separation, explicit control
**Cons**: Requires manual step
```yaml
migrations:
  command: alembic upgrade head
  profiles: [migration]
```

### Option 3: Init Container Pattern
**Pros**: Kubernetes-compatible, clean separation
**Cons**: More complex setup
```yaml
backend:
  depends_on:
    migrations:
      condition: service_completed_successfully
```

## Troubleshooting

### Common Issues
1. **Migration Conflicts**: Multiple developers creating migrations simultaneously
2. **Connection Issues**: Database not ready when migrations run
3. **Permission Issues**: User lacks necessary database permissions

### Solutions
1. **Merge Conflicts**: Use `alembic merge` to resolve conflicts
2. **Health Checks**: Ensure database health check passes before migrations
3. **Permissions**: Grant necessary permissions in `init-db.sql`

## Security Considerations

- **Production Credentials**: Never commit production database URLs
- **Migration User**: Use separate user with DDL permissions for migrations
- **Audit Trail**: Log all migration activities in production
- **Backup Strategy**: Always backup before running migrations

## Response to PR Comment

**Question**: "Puede estar bien, pero donde se corren las migraciones?" (May be OK, but where do migrations run?)

**Answer**:
1. **Current Implementation**: Migrations run automatically when backend starts (line 68 in docker-compose.yml)
2. **Alternative Provided**: Separate migration service available with `--profile migration`
3. **Production Strategy**: Migrations should run as separate deployment step for better control
4. **Full Configuration**: Alembic is properly configured with async support and environment-based settings
