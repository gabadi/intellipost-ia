# ADR-001: Environment Configuration Architecture

**Status:** Accepted
**Date:** 2025-07-03
**Deciders:** Alphonse (Principal Architect)
**Technical Story:** CI/CD Pipeline Failures - Port Configuration Mismatch

## Context

### Problem Statement
The CI/CD pipeline is experiencing failures due to:

1. **Port Configuration Mismatch**: Application configured for port 8000 internally but exposed on port 8080
2. **Environment Variable Loading Issues**: Inconsistent environment variable loading in GitHub Actions
3. **Development/Production Parity**: Different configurations between development and CI environments
4. **Security Scanning Issues**: Bandit reporting false positives on test files

### Current Architecture Issues
- Backend runs on port 8000 internally but Docker exposes 8080
- Frontend expects API on port 8080 but GitHub Actions doesn't load env vars
- No centralized environment configuration strategy
- Inconsistent port mappings across different deployment contexts

## Decision

We will implement a **Hierarchical Environment Configuration Architecture** with the following components:

### 1. Environment Configuration Hierarchy
```
1. Default Values (in settings.py)
2. .env File (development defaults)
3. Environment Variables (runtime overrides)
4. Context-Specific Overrides (CI, Docker, etc.)
```

### 2. Port Standardization Strategy
- **Internal Application Port**: 8000 (consistent across all environments)
- **External Exposed Port**: 8080 (Docker, production)
- **Development Port**: 8000 (direct uvicorn)
- **CI/Testing Port**: 8000 (no Docker port mapping)

### 3. Environment Detection Pattern
```python
Environment Detection:
├── testing (CI/CD, automated tests)
├── development (local development)
├── staging (pre-production)
└── production (live system)
```

## Consequences

### Positive
- **Consistency**: Same configuration pattern across all environments
- **Maintainability**: Single source of truth for configuration
- **Flexibility**: Easy to override for specific contexts
- **Debuggability**: Clear hierarchy for troubleshooting configuration issues

### Negative
- **Migration Required**: Existing configurations need updates
- **Initial Complexity**: More sophisticated configuration management
- **Documentation Overhead**: Need to document all configuration options

## Implementation

### Phase 1: Core Configuration Architecture
1. Update settings.py with environment detection
2. Create environment-specific configuration files
3. Implement configuration validation

### Phase 2: CI/CD Pipeline Updates
1. Update GitHub Actions with proper environment loading
2. Implement context-aware port configuration
3. Fix security scanning exclusions

### Phase 3: Docker Configuration Alignment
1. Standardize port mapping across Docker Compose files
2. Update documentation and README
3. Implement health checks with correct ports

## Alternatives Considered

### Alternative 1: Hard-coded Port Mapping
- **Rejected**: Not flexible enough for different deployment contexts

### Alternative 2: Single .env File for All Environments
- **Rejected**: Security concerns with production credentials in repository

### Alternative 3: Complex Configuration Management System
- **Rejected**: Over-engineering for current application scale

## Implementation Status

- [ ] Core configuration architecture
- [ ] CI/CD pipeline updates
- [ ] Docker configuration alignment
- [ ] Documentation updates
- [ ] Migration testing

## Notes

This ADR addresses the immediate CI/CD failures while establishing a foundation for scalable configuration management as the application grows.
