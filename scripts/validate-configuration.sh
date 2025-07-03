#!/bin/bash
# Configuration Validation Script
# Validates the CI/CD pipeline architecture implementation

set -e

echo "🔍 IntelliPost AI Configuration Validation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation results
ERRORS=0
WARNINGS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ((ERRORS++))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "1. Checking required files..."

# Check if required files exist
required_files=(
    ".env"
    ".env.testing"
    "backend/infrastructure/config/settings.py"
    ".github/workflows/ci.yml"
    "docker-compose.yml"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        print_status 0 "File exists: $file"
    else
        print_status 1 "Missing file: $file"
    fi
done

echo ""
echo "2. Checking port configuration..."

# Check .env.testing port configuration
if grep -q "INTELLIPOST_API_PORT=8000" .env.testing 2>/dev/null; then
    print_status 0 "Testing environment API port configured correctly (8000)"
else
    print_status 1 "Testing environment API port not configured correctly"
fi

# Check GitHub Actions port configuration
if grep -q "INTELLIPOST_API_PORT: 8000" .github/workflows/ci.yml 2>/dev/null; then
    print_status 0 "CI/CD pipeline API port configured correctly (8000)"
else
    print_status 1 "CI/CD pipeline API port not configured correctly"
fi

# Check Docker Compose port mapping
if grep -q '"8080:8000"' docker-compose.yml 2>/dev/null; then
    print_status 0 "Docker port mapping configured correctly (8080:8000)"
else
    print_status 1 "Docker port mapping not configured correctly"
fi

echo ""
echo "3. Checking environment variable consistency..."

# Check if testing environment is properly configured
required_test_vars=(
    "INTELLIPOST_ENVIRONMENT=testing"
    "INTELLIPOST_API_PORT=8000"
    "INTELLIPOST_API_HOST=127.0.0.1"
)

for var in "${required_test_vars[@]}"; do
    if grep -q "$var" .env.testing 2>/dev/null; then
        print_status 0 "Testing variable configured: $var"
    else
        print_status 1 "Missing testing variable: $var"
    fi
done

echo ""
echo "4. Checking GitHub Actions configuration..."

# Check if required environment variables are set in CI
required_ci_vars=(
    "INTELLIPOST_ENVIRONMENT: testing"
    "INTELLIPOST_API_PORT: 8000"
    "INTELLIPOST_DATABASE_URL: postgresql"
)

for var in "${required_ci_vars[@]}"; do
    if grep -q "$var" .github/workflows/ci.yml 2>/dev/null; then
        print_status 0 "CI variable configured: $var"
    else
        print_status 1 "Missing CI variable: $var"
    fi
done

echo ""
echo "5. Checking security scanning configuration..."

# Check Bandit exclusions
if grep -q "exclude='.*tests.*'" .github/workflows/ci.yml 2>/dev/null; then
    print_status 0 "Bandit test exclusions configured"
else
    print_status 1 "Bandit test exclusions not configured"
fi

echo ""
echo "6. Checking Python configuration..."

# Check if settings.py has environment detection
if [[ -f "backend/infrastructure/config/settings.py" ]]; then
    if grep -q "def is_testing" backend/infrastructure/config/settings.py; then
        print_status 0 "Environment detection methods present"
    else
        print_status 1 "Environment detection methods missing"
    fi

    if grep -q "env_file=\[" backend/infrastructure/config/settings.py; then
        print_status 0 "Hierarchical environment file loading configured"
    else
        print_status 1 "Hierarchical environment file loading not configured"
    fi
fi

echo ""
echo "7. Checking Docker configuration consistency..."

# Check if Docker Compose has required environment variables
docker_env_vars=(
    "INTELLIPOST_API_PORT: 8000"
    "INTELLIPOST_API_HOST: 0.0.0.0"
    "VITE_API_URL: http://localhost:8080"
)

for var in "${docker_env_vars[@]}"; do
    if grep -q "$var" docker-compose.yml 2>/dev/null; then
        print_status 0 "Docker environment variable: $var"
    else
        print_status 1 "Missing Docker environment variable: $var"
    fi
done

echo ""
echo "8. Testing Python configuration loading..."

# Test if Python can load the configuration
if command -v python3 &> /dev/null; then
    cd backend 2>/dev/null && {
        if python3 -c "
import sys
sys.path.append('.')
try:
    from infrastructure.config.settings import settings
    print(f'Environment: {settings.environment}')
    print(f'API Port: {settings.api_port}')
    print(f'Testing mode: {settings.is_testing}')
    validation = settings.validate_configuration()
    if all(validation.values()):
        print('Configuration validation: PASSED')
        exit(0)
    else:
        print('Configuration validation: FAILED')
        print(f'Failed checks: {[k for k, v in validation.items() if not v]}')
        exit(1)
except Exception as e:
    print(f'Configuration loading failed: {e}')
    exit(1)
" 2>/dev/null; then
            print_status 0 "Python configuration loading successful"
        else
            print_status 1 "Python configuration loading failed"
        fi
        cd ..
    } || {
        print_warning "Could not test Python configuration (backend directory not accessible)"
    }
else
    print_warning "Python not available for configuration testing"
fi

echo ""
echo "9. Summary"
echo "=========="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 All validations passed! Configuration is ready for CI/CD.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Configuration mostly valid but has $WARNINGS warning(s).${NC}"
    echo "Review warnings above and consider addressing them."
    exit 0
else
    echo -e "${RED}❌ Configuration validation failed with $ERRORS error(s) and $WARNINGS warning(s).${NC}"
    echo "Please address all errors before proceeding with CI/CD pipeline."
    exit 1
fi
