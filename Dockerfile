 # Dockerfile for Audio Transcriber API
FROM python:3.11-slim

 # Build arguments
ARG APP_PORT

 # Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_PORT=${APP_PORT}

 # Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

 # Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

 # Set working directory
WORKDIR /app

 # Copy configuration files
COPY pyproject.toml uv.lock* ./
COPY README.md ./

 # Install uv
RUN pip install uv

 # Copy source code
COPY src/ ./src/
COPY .env.example .env

 # Install dependencies
RUN uv sync --frozen

 # Create cache directory and switch to non-root user
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /app /home/appuser/.cache
USER appuser

 # Expose port dynamically
EXPOSE ${APP_PORT}

 # Default command (can be overridden)
# For API Server: docker run ... (uses default)
# For MCP Server: docker run ... uv run audio-transcriber-mcp
CMD ["sh", "-c", "uv run audio-transcriber server --host 0.0.0.0 --port $APP_PORT"]
