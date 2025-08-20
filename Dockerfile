 # Dockerfile for Audio Transcriber API
FROM python:3.11-slim

# Metadata labels for Docker Hub
LABEL org.opencontainers.image.title="Audio Transcriber" \
      org.opencontainers.image.description="Complete tool for automatic audio file transcription using OpenAI API with REST API and MCP Server support" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Audio Transcriber Team" \
      org.opencontainers.image.url="https://github.com/gianverdum/audio-transcriber" \
      org.opencontainers.image.source="https://github.com/gianverdum/audio-transcriber" \
      org.opencontainers.image.licenses="MIT"

 # Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

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

 # Install uv
RUN pip install uv

 # Copy source code
COPY src/ ./src/

 # Install dependencies
RUN uv sync --frozen

 # Create cache directory and switch to non-root user
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /app /home/appuser/.cache
USER appuser

 # Expose port
EXPOSE 8000

 # Default command (can be overridden)
# For API Server: docker run ... (uses default)
# For MCP Server: docker run ... uv run audio-transcriber-mcp
CMD ["sh", "-c", "uv run audio-transcriber server --host 0.0.0.0 --port 8000"]
