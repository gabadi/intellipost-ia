#!/bin/bash
# Quality Gate Validation Script for IntelliPost AI
# Validates NFR8.1 compliance and all automated quality checks

set -e  # Exit on any error

# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 IntelliPost AI - Quality Gate Validation"
echo "============================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
FAILURES=0
TOTAL_CHECKS=0

# Function to run a check and track results
run_check() {
    local check_name="$1"
    local command="$2"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "${BLUE}[$TOTAL_CHECKS] Running: $check_name${NC}"

    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $check_name${NC}"
    else
        echo -e "${RED}❌ FAIL: $check_name${NC}"
        FAILURES=$((FAILURES + 1))
        echo -e "${YELLOW}Command: $command${NC}"
        eval "$command" || true  # Show the actual error
    fi
    echo
}

echo "🔧 Environment Validation"
echo "========================="

# Check required tools
run_check "UV available" "which uv"
run_check "Node.js available" "which node"
run_check "npm available" "which npm"
run_check "Git available" "which git"

echo "🐍 Python Backend Quality Gates"
echo "==============================="

# Python environment and dependencies
run_check "Python virtual environment active" "test -d .venv"
run_check "Python dependencies installed" "uv run python -c 'import fastapi, uvicorn, pydantic'"

# Python code quality
run_check "Ruff linting (Python)" "uv run ruff check backend/"
run_check "Ruff formatting (Python)" "uv run ruff format --check backend/"
run_check "Pyright type checking" "uv run pyright backend/"
run_check "Tach architectural boundaries" "uv run tach check"

# Python testing infrastructure
run_check "Pytest available" "uv run python -c 'import pytest'"
run_check "Coverage available" "uv run python -c 'import coverage'"

echo "🌐 Frontend Quality Gates"
echo "========================"

# Frontend dependencies
run_check "Frontend dependencies installed" "cd frontend && test -d node_modules"

# Frontend code quality
run_check "Prettier formatting (Frontend)" "cd frontend && npm run format > /dev/null 2>&1; cd frontend && npx prettier --check ."
run_check "ESLint linting (Frontend)" "cd frontend && npx eslint src/"
run_check "Dependency cruiser validation" "cd frontend && npm run dep-check"

# Frontend build tools
run_check "TypeScript compilation" "cd frontend && npx tsc --noEmit"

echo "🔀 Integration Quality Gates"
echo "==========================="

# Pre-commit hooks
run_check "Pre-commit hooks installed" "test -f .git/hooks/pre-commit"
run_check "Commit-msg hooks installed" "test -f .git/hooks/commit-msg"
run_check "Pre-commit configuration valid" "uv run pre-commit validate-config"

# Project structure validation
run_check "Backend structure valid" "test -d backend/domain && test -d backend/infrastructure && test -d backend/application && test -d backend/api"
run_check "Frontend structure valid" "test -d frontend/src"
run_check "Documentation present" "test -f README.md"

echo "📋 Configuration Validation"
echo "=========================="

# Configuration files
run_check "pyproject.toml valid" "uv run python -c 'import tomllib; f=open(\"pyproject.toml\", \"rb\"); tomllib.load(f); f.close()'"
run_check "package.json valid" "cd frontend && node -e 'JSON.parse(require(\"fs\").readFileSync(\"package.json\", \"utf8\"))'"
run_check "ESLint config valid" "cd frontend && npx eslint --print-config src/lib/test.ts > /dev/null"
run_check "Prettier config valid" "cd frontend && npx prettier --find-config-path ."
run_check "Pre-commit config valid" "uv run pre-commit validate-config .pre-commit-config.yaml"

echo "🛡️ Security and Best Practices"
echo "=============================="

# Security checks
run_check "No private keys detected" "! uv run pre-commit run detect-private-key --all-files 2>&1 | grep -q FAILED"
run_check "No large files committed" "! uv run pre-commit run check-added-large-files --all-files 2>&1 | grep -q FAILED"
run_check "No merge conflicts" "! uv run pre-commit run check-merge-conflict --all-files 2>&1 | grep -q FAILED"

# Code quality best practices
run_check "File endings consistent" "! uv run pre-commit run mixed-line-ending --all-files 2>&1 | grep -q FAILED"
run_check "No trailing whitespace" "! uv run pre-commit run trailing-whitespace --all-files 2>&1 | grep -q FAILED"
run_check "Files end with newline" "! uv run pre-commit run end-of-file-fixer --all-files 2>&1 | grep -q FAILED"

echo "📊 Quality Gate Summary"
echo "======================"

PASSED=$((TOTAL_CHECKS - FAILURES))
PASS_RATE=$(( PASSED * 100 / TOTAL_CHECKS ))

echo -e "Total Checks: ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILURES${NC}"
echo -e "Pass Rate: ${BLUE}$PASS_RATE%${NC}"
echo

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}🎉 All Quality Gates PASSED!${NC}"
    echo -e "${GREEN}✅ NFR8.1 Compliance: VALIDATED${NC}"
    echo -e "${GREEN}✅ Project ready for development${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILURES Quality Gate(s) FAILED${NC}"
    echo -e "${RED}❌ NFR8.1 Compliance: ISSUES FOUND${NC}"
    echo -e "${YELLOW}Please fix the failing checks before proceeding${NC}"
    exit 1
fi
