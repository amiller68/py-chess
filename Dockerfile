FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY uv.lock pyproject.toml ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create startup script that runs migrations then starts server
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "Running database migrations..."' >> /app/start.sh && \
    echo 'uv run alembic upgrade head' >> /app/start.sh && \
    echo 'echo "Starting server..."' >> /app/start.sh && \
    echo 'exec uv run python -m src' >> /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/app/start.sh"]
