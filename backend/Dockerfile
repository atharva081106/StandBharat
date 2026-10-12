# Multi-stage production Dockerfile for StandBharat Backend
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.10-slim AS runner

WORKDIR /app

# Install runtime PostgreSQL client library, tools (pg_dump/pg_restore) & curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user
RUN groupadd -g 1001 standbharat && \
    useradd -u 1001 -g standbharat -s /bin/bash -m standbharat

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/standbharat/.local
ENV PATH=/home/standbharat/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create storage directory with appropriate ownership
RUN mkdir -p /app/storage/documents /app/storage/backups && chown -R standbharat:standbharat /app

# Copy application source code
COPY --chown=standbharat:standbharat . /app

USER standbharat

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
