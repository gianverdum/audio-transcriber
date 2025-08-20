# Audio Transcriber - AI Coding Agent Guide

## Project Architecture Overview

**Audio Transcriber** is a multi-interface OpenAI Whisper transcription service with 5 distinct deployment patterns:
- **CLI** (`audio-transcriber transcribe ./audios`) - Local batch processing
- **REST API** (`audio-transcriber server`) - FastAPI web service with authentication
- **Docker** (`docker compose up`) - Multi-profile containerized deployment  
- **AWS Lambda** - Serverless cloud deployment
- **MCP Server** (`audio-transcriber-mcp`) - Model Context Protocol for AI agents (stdio/HTTP modes)

### Core Components

- **`src/audio_transcriber/core/`** - Business logic
  - `transcriber.py` - Main `AudioTranscriber` class with OpenAI integration
  - `config.py` - Centralized configuration via `.env` with authentication
- **`src/audio_transcriber/api/`** - FastAPI web layer with Bearer token auth
  - `main.py` - FastAPI app with HTTPBearer authentication middleware
  - `service.py` - API-specific business logic
  - `models.py` - Pydantic request/response models
- **`src/audio_transcriber/mcp/`** - MCP Server for AI agents
  - `server.py` - MCP protocol implementation (stdio and HTTP modes)
  - `service.py` - URL-based transcription logic with download handling
  - `models.py` - MCP-specific data models
- **`src/audio_transcriber/cli.py`** - Command-line interface with dual-mode support

## Essential Development Patterns

### Configuration Philosophy
**Everything is `.env`-driven with sensible defaults and authentication.** The `Settings` class in `config.py` centralizes all configuration:

```python
# All components use settings.VARIABLE_NAME
from audio_transcriber.core.config import settings
uvicorn.run(host=settings.SERVER_HOST, port=settings.SERVER_PORT)
```

**Authentication**: Bearer token via `AUTH_TOKEN` environment variable. FastAPI uses `HTTPBearer` dependency injection.

**Never hardcode values** - always reference `settings` or provide CLI overrides.

### Docker Architecture
**Multi-profile deployment** with simplified environment variable approach:
- **Local development**: `docker-compose.yml` (port 8001)
- **Production (Portainer)**: `docker-compose.portainer.yml` with Traefik integration, overlay networks, and health checks
- **Environment variables**: No Docker secrets - all configuration via `.env` file
- **Multi-service**: API server + MCP HTTP server in separate containers

### Dependency Management
**This project uses `uv` (not pip/poetry).** All Python commands must be prefixed with `uv run`:

```bash
uv run audio-transcriber server          # NOT: python -m audio_transcriber
uv run pytest                           # NOT: pytest
uv run python scripts/test_api.py       # NOT: python scripts/test_api.py
```

### CLI Dual-Mode Pattern
The CLI supports both explicit commands and legacy compatibility:
```bash
# Modern syntax
uv run audio-transcriber transcribe ./audios -o output.xlsx
uv run audio-transcriber server --host 0.0.0.0 --port 8000

# Legacy compatibility (for backward compatibility)
uv run audio-transcriber ./audios -o output.xlsx
```

### MCP Server Pattern
The MCP (Model Context Protocol) server enables AI agents to transcribe audio from URLs:
```bash
# Start MCP stdio server for AI agent integration
uv run audio-transcriber-mcp

# Start MCP HTTP server for remote access
uv run audio-transcriber-mcp-http
# Access: http://localhost:8003/mcp/v1
```

**Key difference**: MCP accepts URLs instead of file uploads, perfect for WhatsApp/messaging integration.

**Available modes**:
- **stdio**: Direct communication with AI agents (Claude Desktop, etc.)
- **HTTP**: Remote access for cloud-based AI agents (production)
### Error Handling Pattern
The codebase uses a consistent tuple return pattern for operations:
```python
transcription, success, error = transcriber.transcribe_audio(file_path)
# Always returns (result, bool, error_message)
```

## Critical Developer Workflows

### Local Development Server
```bash
# Development with auto-reload
uv run audio-transcriber server --reload

# Production-like (no reload, multiple workers) 
uv run audio-transcriber server --host 0.0.0.0 --workers 4

# MCP stdio server for AI agents
uv run audio-transcriber-mcp

# MCP HTTP server for remote access
uv run audio-transcriber-mcp-http
```

### Testing Strategy
- **Unit tests**: `uv run pytest tests/`
- **API testing**: `uv run python scripts/test_api.py` (requires running server)
- **Configuration validation**: `uv run python scripts/test_config.py`
- **Environment setup**: `uv run python scripts/test_env.py`
- **Comprehensive validation**: `uv run python scripts/test_final_validation.py`

### Docker Development
**Environment variables only** (no Docker secrets for simplicity):
```bash
# Local development (port 8001)
docker compose up

# Production deployment (Portainer with Traefik)
docker compose -f docker-compose.portainer.yml up
```

**Docker port requires rebuild when changed** (it's a build argument):
```bash
# After changing DOCKER_PORT in .env
docker compose build && docker compose up
```

## Integration Points & Dependencies

### OpenAI API Integration
- **Rate limiting**: Built-in 0.5s delay between requests (configurable via `API_DELAY`)
- **File size limits**: 25MB OpenAI hard limit (configurable via `MAX_FILE_SIZE_MB`)
- **Timeout handling**: 30s default timeout (configurable via `API_TIMEOUT`)

### Output Format Architecture
The system supports multiple output formats through a unified interface:
- **Excel** (`.xlsx`) - Default with two sheets: "Transcriptions" + "Summary"
- **CSV** - Tabular data export
- **JSON** - Structured API responses
- **TXT** - Plain text transcriptions

### MCP Server Integration
- **URL-based processing**: Downloads audio from URLs (essential for WhatsApp/messaging)
- **Dual mode support**: stdio for direct AI agent communication, HTTP for remote access
- **AI agent protocol**: Uses stdio communication for MCP clients
- **Async architecture**: Handles concurrent downloads and transcriptions
- **Error resilience**: Graceful handling of download failures and invalid URLs
- **Health monitoring**: HTTP mode includes `/health` endpoint
### AWS Lambda Deployment
Uses **Mangum** to wrap FastAPI for Lambda. Key considerations:
- 15-minute Lambda timeout (set in `template.yaml`)
- Environment variables passed through CloudFormation parameters
- S3 bucket for temporary file storage (lifecycle: 1 day retention)

## Project-Specific Conventions

### File Structure Patterns
```
src/audio_transcriber/
├── core/           # Business logic (pure Python)
├── api/           # Web layer (FastAPI)
├── mcp/           # MCP Server (AI agents protocol)
└── cli.py         # Command-line interface
```

### Logging Strategy
- Uses Python `logging` module with configurable levels
- File logging optional via `SAVE_LOGS=true`
- Structured logs include processing time, file info, success/failure

### Supported Audio Formats
Hardcoded in `AudioTranscriber.SUPPORTED_FORMATS` set:
```python
{'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
```

## Development Commands Reference

```bash
# Setup and testing
uv sync                                    # Install all dependencies
uv run python scripts/test_config.py      # Validate .env configuration
uv run python scripts/test_api.py         # Test running API server

# Development server
uv run audio-transcriber server --reload  # Development with auto-reload
uv run audio-transcriber server           # Uses .env settings

# CLI usage
uv run audio-transcriber transcribe ./audios -o result.xlsx
uv run audio-transcriber transcribe ./audios --language pt

# MCP Server (for AI agents)
uv run audio-transcriber-mcp                  # Start MCP stdio server
uv run audio-transcriber-mcp-http             # Start MCP HTTP server

# Docker workflows  
docker compose up                          # Auto-loads .env
docker compose build                      # Required after DOCKER_PORT changes

# AWS deployment
cd aws && ./deploy.sh                     # SAM-based deployment

# Testing and validation
uv run pytest                            # Run all unit tests
uv run python scripts/test_final_validation.py  # Comprehensive validation
```

## Key Implementation Details

- **Centralized config**: All settings flow through `audio_transcriber.core.config.settings`
- **Async API**: FastAPI endpoints are async but core transcriber is sync (wrapped in async)
- **Excel output**: Uses `openpyxl` with custom formatting (column widths, dual sheets)
- **Health checks**: `/health` endpoint validates OpenAI connectivity
- **CORS enabled**: API allows all origins (configure for production)
- **MCP protocol**: Uses stdio for AI agent communication and HTTP for remote access
- **URL validation**: MCP server validates and downloads from URLs before processing
- **Authentication**: Bearer token authentication via `AUTH_TOKEN` environment variable
- **Multi-service deployment**: Supports both API and MCP servers in separate containers

When modifying this codebase:
1. **Always use `uv run`** for Python commands
2. **Reference `settings.VARIABLE`** instead of hardcoding
3. **Follow the tuple return pattern** for error handling
4. **Test both CLI and API interfaces** when changing core logic
5. **Update both documentation endpoints** (`/docs`, `/redoc`) for API changes
6. **Test MCP server** with `uv run audio-transcriber-mcp` for AI agent integration
7. **Run comprehensive validation** with `uv run python scripts/test_final_validation.py`
8. **Rebuild Docker after configuration changes** affecting build arguments
