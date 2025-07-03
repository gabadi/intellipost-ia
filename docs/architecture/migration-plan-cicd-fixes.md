# Migration Plan: CI/CD Pipeline Architecture Fixes

## Executive Summary

This migration plan addresses the critical CI/CD pipeline failures caused by port configuration mismatches and environment variable loading issues. The implementation follows the architectural decisions outlined in ADR-001.

## Pre-Migration Checklist

### 1. Backup Current Configuration
- [ ] Backup current `.env` file
- [ ] Backup current `docker-compose.yml`
- [ ] Backup current GitHub Actions workflow
- [ ] Document current port mappings

### 2. Environment Verification
- [ ] Verify local development environment works
- [ ] Document current test execution behavior
- [ ] Note any existing CI/CD failures

### 3. Team Communication
- [ ] Notify development team of migration window
- [ ] Share migration plan with stakeholders
- [ ] Prepare rollback plan

## Migration Steps

### Phase 1: Core Configuration Updates (Estimated: 2 hours)

#### Step 1.1: Update Settings Configuration
✅ **COMPLETED** - Updated `backend/infrastructure/config/settings.py`:
- Added environment detection properties
- Implemented hierarchical environment file loading
- Added configuration validation methods
- Enhanced API URL generation

#### Step 1.2: Create Testing Environment Configuration
✅ **COMPLETED** - Created `.env.testing`:
- Standardized port configuration (8000)
- Test-specific database settings
- Disabled external API calls for testing
- Reduced resource settings for CI

#### Step 1.3: Update GitHub Actions Workflow
✅ **COMPLETED** - Updated `.github/workflows/ci.yml`:
- Added explicit environment variables for testing
- Fixed port configuration to use 8000
- Enhanced security scanning exclusions
- Improved test environment setup

### Phase 2: Docker Configuration Alignment (Estimated: 1 hour)

#### Step 2.1: Update Docker Compose Files
✅ **COMPLETED** - Updated `docker-compose.yml`:
- Added explicit API port and host environment variables
- Ensured consistent port mapping (8080:8000)
- Updated frontend environment variables

#### Step 2.2: Verify Docker Configuration
- [ ] Test Docker Compose services start correctly
- [ ] Verify port accessibility
- [ ] Test frontend-backend communication

### Phase 3: Testing and Validation (Estimated: 2 hours)

#### Step 3.1: Local Testing
```bash
# Test local development environment
npm run dev:backend &
npm run dev:frontend &
curl http://localhost:8000/health
curl http://localhost:4000

# Test Docker environment
docker compose up -d postgres minio
docker compose --profile migration run --rm migrations
docker compose up backend frontend
curl http://localhost:8080/health
curl http://localhost:4000
```

#### Step 3.2: CI/CD Pipeline Testing
- [ ] Create test branch with changes
- [ ] Push to trigger CI/CD pipeline
- [ ] Verify all pipeline steps pass
- [ ] Check test coverage reporting

#### Step 3.3: Integration Testing
- [ ] Test API connectivity on correct ports
- [ ] Verify database connections
- [ ] Test security scanning passes
- [ ] Verify frontend builds and connects to API

### Phase 4: Documentation Updates (Estimated: 1 hour)

#### Step 4.1: Update README.md
- [ ] Update port information
- [ ] Update service URLs
- [ ] Update troubleshooting section

#### Step 4.2: Update Architecture Documentation
- [ ] Update deployment strategy
- [ ] Update API specification
- [ ] Update development setup instructions

## Implementation Scripts

### Script 1: Pre-Migration Backup
```bash
#!/bin/bash
# backup-current-config.sh

echo "Backing up current configuration..."
mkdir -p migration-backup/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="migration-backup/$(date +%Y%m%d_%H%M%S)"

cp .env "$BACKUP_DIR/.env.backup"
cp docker-compose.yml "$BACKUP_DIR/docker-compose.yml.backup"
cp .github/workflows/ci.yml "$BACKUP_DIR/ci.yml.backup"
cp backend/infrastructure/config/settings.py "$BACKUP_DIR/settings.py.backup"

echo "Backup completed in $BACKUP_DIR"
```

### Script 2: Validation Script
```bash
#!/bin/bash
# validate-configuration.sh

echo "Validating configuration..."

# Check if required files exist
files=(".env.testing" "backend/infrastructure/config/settings.py" ".github/workflows/ci.yml")
for file in "${files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Required file $file not found"
        exit 1
    fi
done

# Check port configuration
if grep -q "INTELLIPOST_API_PORT=8000" .env.testing; then
    echo "✓ Testing port configuration correct"
else
    echo "ERROR: Testing port configuration incorrect"
    exit 1
fi

# Check GitHub Actions environment variables
if grep -q "INTELLIPOST_API_PORT: 8000" .github/workflows/ci.yml; then
    echo "✓ CI/CD port configuration correct"
else
    echo "ERROR: CI/CD port configuration incorrect"
    exit 1
fi

echo "Configuration validation completed successfully"
```

### Script 3: Test Environment Verification
```bash
#!/bin/bash
# test-environment.sh

echo "Testing environment configuration..."

# Start services
echo "Starting test services..."
docker compose up -d postgres

# Wait for postgres to be ready
echo "Waiting for database..."
until docker compose exec postgres pg_isready -U intellipost_user -d intellipost_dev; do
    sleep 2
done

# Test backend startup
echo "Testing backend startup..."
cd backend
INTELLIPOST_ENVIRONMENT=testing uv run python -c "
from infrastructure.config.settings import settings
print(f'Environment: {settings.environment}')
print(f'API Port: {settings.api_port}')
print(f'Database URL: {settings.get_database_url()}')
validation = settings.validate_configuration()
print(f'Configuration valid: {all(validation.values())}')
"

# Test API health check
echo "Testing API health..."
cd backend
INTELLIPOST_ENVIRONMENT=testing uv run uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
sleep 5

if curl -f http://localhost:8000/health; then
    echo "✓ API health check passed"
else
    echo "ERROR: API health check failed"
    kill $BACKEND_PID
    exit 1
fi

kill $BACKEND_PID
cd ..

echo "Environment testing completed successfully"
```

## Rollback Plan

### Immediate Rollback (if issues detected)
```bash
# Restore from backup
BACKUP_DIR="migration-backup/$(ls -t migration-backup/ | head -n 1)"
cp "$BACKUP_DIR/.env.backup" .env
cp "$BACKUP_DIR/docker-compose.yml.backup" docker-compose.yml
cp "$BACKUP_DIR/ci.yml.backup" .github/workflows/ci.yml
cp "$BACKUP_DIR/settings.py.backup" backend/infrastructure/config/settings.py

# Remove new files
rm -f .env.testing

# Restart services
docker compose down
docker compose up -d
```

### Gradual Rollback (if issues found after deployment)
1. Revert GitHub Actions workflow first
2. Test CI/CD pipeline
3. If still failing, revert settings.py changes
4. If still failing, revert Docker configuration

## Risk Assessment

### High Risk Items
1. **Database connectivity**: Changes to database URL format
   - **Mitigation**: Thorough testing, immediate rollback capability
2. **API accessibility**: Port configuration changes
   - **Mitigation**: Validate all endpoints, test with frontend

### Medium Risk Items
1. **CI/CD pipeline stability**: New environment variables
   - **Mitigation**: Test on feature branch first
2. **Docker container startup**: Environment variable changes
   - **Mitigation**: Local Docker testing before deployment

### Low Risk Items
1. **Documentation accuracy**: README updates
   - **Mitigation**: Review and team validation

## Success Criteria

### Functional Requirements
- [ ] CI/CD pipeline passes all stages
- [ ] Local development environment works unchanged
- [ ] Docker environment starts and functions correctly
- [ ] API accessible on documented ports
- [ ] Frontend connects to backend successfully
- [ ] All tests pass in CI/CD environment

### Performance Requirements
- [ ] CI/CD pipeline completes in < 10 minutes
- [ ] Application startup time unchanged
- [ ] Test execution time unchanged or improved

### Quality Requirements
- [ ] Security scanning passes without false positives
- [ ] Type checking passes
- [ ] Code coverage reporting works
- [ ] Architecture validation passes

## Post-Migration Tasks

### Immediate (Day 1)
- [ ] Monitor CI/CD pipeline for any failures
- [ ] Verify all team members can develop locally
- [ ] Check production deployment pipeline

### Short-term (Week 1)
- [ ] Update onboarding documentation
- [ ] Train team on new configuration patterns
- [ ] Create troubleshooting guide

### Long-term (Month 1)
- [ ] Implement configuration monitoring
- [ ] Add automated configuration validation
- [ ] Plan for production deployment with new architecture

## Communication Plan

### Before Migration
- Send migration notice 24 hours in advance
- Share migration plan with development team
- Prepare troubleshooting contacts

### During Migration
- Real-time updates in team chat
- Document any issues encountered
- Maintain rollback readiness

### After Migration
- Confirm successful completion
- Share validation results
- Document lessons learned

## Support and Troubleshooting

### Common Issues and Solutions

#### Issue: "Connection refused on port 8080"
**Solution**: Check if Docker port mapping is active, ensure container is running

#### Issue: "Environment variable not loaded"
**Solution**: Verify `.env.testing` file exists and has correct permissions

#### Issue: "Bandit security scan failures"
**Solution**: Ensure test files are properly excluded in bandit configuration

#### Issue: "Database connection failed"
**Solution**: Verify PostgreSQL service is running and URL format is correct

### Emergency Contacts
- Principal Architect: Alphonse
- DevOps Infrastructure Specialist: Alex
- Development Team Lead: [To be assigned]

## Validation Checklist

### Pre-Deployment Validation
- [ ] All files backed up
- [ ] Validation scripts pass
- [ ] Test environment verified
- [ ] Team notified

### Post-Deployment Validation
- [ ] CI/CD pipeline successful
- [ ] Local development functional
- [ ] Docker environment functional
- [ ] API endpoints accessible
- [ ] Frontend-backend communication working
- [ ] All tests passing
- [ ] Security scans passing
- [ ] Documentation updated

### Final Sign-off
- [ ] Principal Architect approval
- [ ] DevOps Infrastructure Specialist approval
- [ ] Development Team Lead approval
- [ ] Product Owner notification
