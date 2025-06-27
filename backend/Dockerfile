# Use Python 3.13 slim image for latest performance and security improvements
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH=/app/.venv/bin:$PATH \
    UV_CACHE_DIR=/tmp/uv-cache

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install UV for fast dependency management
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Create docker-specific virtual environment to avoid conflicts
RUN uv venv .venv_docker && uv sync --no-dev

# Expose port
EXPOSE 8000

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create cache directory for UV and set permissions
RUN mkdir -p /tmp/uv-cache && chown -R appuser:appuser /tmp/uv-cache

# Create a startup script to properly activate the docker virtual environment
RUN echo '#!/bin/bash\nsource /app/.venv_docker/bin/activate\nexec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Change ownership to non-root user (including the entrypoint script)
RUN chown -R appuser:appuser /app
USER appuser

# Health check using Python instead of curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Set entrypoint to activate virtual environment
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application with optimized settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop"]
