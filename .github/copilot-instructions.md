# Audio Transcriber - AI Coding Agent Guide

## Project Architecture Overview

**Audio Transcriber** is a multi-interface OpenAI Whisper transcription service with 4 distinct deployment patterns:
- **CLI** (`audio-transcriber transcribe ./audios`) - Local batch processing
- **REST API** (`audio-transcriber server`) - FastAPI web service  
- **Docker** (`docker compose up`) - Containerized deployment
- **AWS Lambda** - Serverless cloud deployment

### Core Components

- **`src/audio_transcriber/core/`** - Business logic
  - `transcriber.py` - Main `AudioTranscriber` class with OpenAI integration
  - `config.py` - Centralized configuration via `.env` (Settings class)
- **`src/audio_transcriber/api/`** - FastAPI web layer
  - `main.py` - FastAPI app with comprehensive endpoints
  - `service.py` - API-specific business logic
  - `models.py` - Pydantic request/response models
- **`src/audio_transcriber/cli.py`** - Command-line interface with dual-mode support

## Essential Development Patterns

### Configuration Philosophy
**Everything is `.env`-driven with sensible defaults.** The `Settings` class in `config.py` centralizes all configuration:

```python
# All components use settings.VARIABLE_NAME
from audio_transcriber.core.config import settings
uvicorn.run(host=settings.SERVER_HOST, port=settings.SERVER_PORT)
```

**Never hardcode values** - always reference `settings` or provide CLI overrides.

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
```

### Testing Strategy
- **Unit tests**: `uv run pytest tests/`
- **API testing**: `uv run python scripts/test_api.py` (requires running server)
- **Configuration validation**: `uv run python scripts/test_config.py`
- **Environment setup**: `uv run python scripts/test_env.py`

### Docker Development
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

# Docker workflows  
docker compose up                          # Auto-loads .env
docker compose build                      # Required after DOCKER_PORT changes

# AWS deployment
cd aws && ./deploy.sh                     # SAM-based deployment
```

## Key Implementation Details

- **Centralized config**: All settings flow through `audio_transcriber.core.config.settings`
- **Async API**: FastAPI endpoints are async but core transcriber is sync (wrapped in async)
- **Excel output**: Uses `openpyxl` with custom formatting (column widths, dual sheets)
- **Health checks**: `/health` endpoint validates OpenAI connectivity
- **CORS enabled**: API allows all origins (configure for production)

When modifying this codebase:
1. **Always use `uv run`** for Python commands
2. **Reference `settings.VARIABLE`** instead of hardcoding
3. **Follow the tuple return pattern** for error handling
4. **Test both CLI and API interfaces** when changing core logic
5. **Update both documentation endpoints** (`/docs`, `/redoc`) for API changes
