 # Dockerfile for Audio Transcriber API
FROM python:3.11-slim

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
COPY .env.example .env

 # Install dependencies
RUN uv sync --frozen

 # Switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

 # Expose port
EXPOSE 8000

 # Default command
CMD ["uv", "run", "uvicorn", "audio_transcriber.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
