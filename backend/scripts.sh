#!/bin/bash
# Development scripts for IntelliPost AI Backend
# Usage: source scripts.sh

# Test commands
alias test-unit="uv run pytest -m unit -v"
alias test-integration="uv run pytest -m integration -v" 
alias test-all="uv run pytest -v"
alias test-unit-fast="uv run pytest -m unit -q"
alias test-integration-fast="uv run pytest -m integration -q"

# Quality commands
alias lint="uvx ruff check ."
alias format="uvx ruff format ."
alias typecheck="uv run pyright"
alias check-arch="uvx tach check"
alias security="uvx bandit -r modules/ infrastructure/ api/ --exclude='*/tests/*,*/test_*.py,*/fixtures/*' --skip=B101,B601,B105,B106,B110"

# Combined commands
quality-check() {
    echo "🔍 Running quality checks..."
    lint && typecheck && check-arch && security
}

ci-check() {
    echo "🚀 Running full CI pipeline..."
    quality-check && test-unit && test-integration
}

echo "✅ Development scripts loaded!"
echo "📋 Available commands:"
echo "  Test: test-unit, test-integration, test-all, test-unit-fast, test-integration-fast"
echo "  Quality: lint, format, typecheck, check-arch, security"
echo "  Combined: quality-check, ci-check"
echo ""
echo "💡 Usage: test-unit-fast  # Fast unit tests"
echo "💡 Usage: quality-check   # All quality checks"