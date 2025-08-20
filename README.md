# 🎵 Audio Transcriber

Complete tool for automatic audio file transcription using OpenAI API, available as:

- **📱 CLI** - Command line interface
- **🌐 REST API** - Web server with FastAPI  
- **☁️ AWS Lambda** - Serverless cloud deployment
- **🐳 Docker** - Container for development and production
- **🔗 MCP Server** - Model Context Protocol for AI agents integration

## 📋 Features

- **Automatic transcription** using OpenAI's Whisper model
- **Multiple input formats**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, OGG, FLAC
- **Multiple output formats**: JSON, TXT, Excel (XLSX), CSV
- **Complete REST API** with automatic documentation
- **Batch processing support**
- **AWS Lambda ready deployment**
- **Docker container** for easy deployment
- **MCP Server** for AI agents integration (WhatsApp, messaging platforms)
- **URL-based transcription** for remote audio files
- **Secure credentials system** with .env files
- **Robust error handling** and detailed logging

## 🚀 Installation

### Prerequisites

This project uses **[uv](https://docs.astral.sh/uv/)** for Python dependency management. If you don't have `uv` installed yet:

```bash
# Install uv (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Option 1: Using UV (Recommended)

```bash
# Clone the project
git clone <repository_url>
cd audio-transcriber

# Sync and install all dependencies
uv sync
```

### Option 2: Using traditional pip

```bash
# Clone the project
git clone <repository_url>
cd audio-transcriber

# Install dependencies
pip install -e .
```

### OpenAI API Configuration

Audio Transcriber uses `.env` file to manage credentials securely.

**Step 1: Create configuration file**
```bash
# Copy the example file
cp .env.example .env

# Or use the utility script
uv run python scripts/setup_env.py
```

**Step 2: Configure your credentials and preferences**
1. Get your key at: https://platform.openai.com/account/api-keys
2. Edit the `.env` file and configure:
   ```bash
   # REQUIRED - OpenAI API Configuration
   OPENAI_API_KEY=sk-proj-your_real_key_here
   
   # API Server Configuration (optional)
   SERVER_HOST=0.0.0.0
   SERVER_PORT=8000
   DOCKER_PORT=8001
   MCP_DOCKER_PORT=8002
   
   # Processing Configuration (optional)
   MAX_FILE_SIZE_MB=25
   LOG_LEVEL=INFO
   
   # Development Configuration (optional)
   # SERVER_RELOAD=false
   # DEBUG=false
   ```

**Alternative: Environment variable**
```bash
export OPENAI_API_KEY="your_openai_key_here"
```

> **⚠️ Important:** Never commit the `.env` file to git. It's already included in `.gitignore`.

## ⚙️ Centralized Configuration

Audio Transcriber uses a centralized configuration system through the `.env` file. All configurations have sensible defaults and can be customized as needed.

### � Mandatory Configuration
```bash
# OpenAI API key (REQUIRED)
OPENAI_API_KEY=sk-proj-your_real_key_here
```

### �📡 Server Configuration (optional)
```bash
# Server host (default: 0.0.0.0)
SERVER_HOST=0.0.0.0

# Server port (default: 8000)
SERVER_PORT=8000

# Number of workers (default: 1)
SERVER_WORKERS=1

# Auto-reload for development (default: false)
SERVER_RELOAD=true
```

### 🎵 API Configurations
```bash
# API title (default: Audio Transcriber API)
API_TITLE=My Transcription API

# API version (default: 1.0.0)
API_VERSION=2.0.0

# API description
API_DESCRIPTION=Custom API for audio transcription
```

### ⚙️ Processing Configurations
```bash
# Maximum file size in MB (default: 25)
MAX_FILE_SIZE_MB=50

# Timeout for OpenAI requests in seconds (default: 30)
API_TIMEOUT=60

# Delay between requests in seconds (default: 0.5)
API_DELAY=1.0
```

### 📁 Directory Configurations
```bash
# Default folder for audio files (default: ./audios)
DEFAULT_AUDIO_FOLDER=./my_audios

# Default folder for output files (default: ./output)
DEFAULT_OUTPUT_FOLDER=./results
```

### 🐛 Debug and Log Configurations
```bash
# Log level (default: INFO) - values: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=DEBUG

# Debug mode (default: false)
DEBUG=true

# Save logs to file (default: false)
SAVE_LOGS=true
```

### 🔧 Testing and Verifying Configurations
```bash
# View all loaded configurations
uv run python scripts/test_config.py

# Test server with .env configurations
uv run audio-transcriber server

# CLI Temporary Override (always override .env)
uv run audio-transcriber server --port 9000 --host 0.0.0.0 --reload

# Verify if configuration is set correctly
uv run python -c "from audio_transcriber.core.config import settings; print(f'Port: {settings.SERVER_PORT}, Host: {settings.SERVER_HOST}')"
```

### 📋 Complete Configurations Table

| Variable | Type | Default | Description |
|----------|------|--------|-----------|
| **MANDATORY** |
| `OPENAI_API_KEY` | string | - | OpenAI API Key |
| **SERVER** |
| `SERVER_HOST` | string | `0.0.0.0` | Server Host |
| `SERVER_PORT` | int | `8000` | Server Port |
| `SERVER_WORKERS` | int | `1` | Number of Workers |
| `SERVER_RELOAD` | bool | `false` | Auto-reload development |
| **DOCKER** |
| `DOCKER_PORT` | int | `8001` | Docker exposed port (requires rebuild) |
| `MCP_DOCKER_PORT` | int | `8002` | MCP Server Docker port (requires rebuild) |
| `MCP_SERVER_HOST` | string | `0.0.0.0` | MCP HTTP Server host |
| `MCP_SERVER_PORT` | int | `8003` | MCP HTTP Server port |
| **API** |
| `API_TITLE` | string | `Audio Transcriber API` | API Title |
| `API_VERSION` | string | `1.0.0` | API Version |
| `API_DESCRIPTION` | string | `API perform...` | API Description |
| **PROCESSING** |
| `MAX_FILE_SIZE_MB` | int | `25` | Max File Size |
| `API_TIMEOUT` | int | `30` | Timeout requests OpenAI |
| `API_DELAY` | float | `0.5` | Delay between requests |
| **DIRECTORIES** |
| `DEFAULT_AUDIO_FOLDER` | string | `./audios` | Default audios folder |
| `DEFAULT_OUTPUT_FOLDER` | string | `./output` | Default output folder |
| **DEBUG** |
| `LOG_LEVEL` | string | `INFO` | Log Level |
| `DEBUG` | bool | `false` | Debug Mode |
| `SAVE_LOGS` | bool | `false` | Save Logs in File |

> **💡 Tip:** Values of type `bool` should be `true` or `false` (lower case). Commented values `#` use setup default.

> **🐳 Docker Note:** Changing `DOCKER_PORT` or `MCP_DOCKER_PORT` requires rebuilding the Docker image with `docker compose build` because the ports are set as build arguments.

## 📖 How to Use

### 1️⃣ CLI (Command Line)

```bash
# Local transcription (traditional mode)
uv run audio-transcriber transcribe /path/to/audio/folder
uv run audio-transcriber transcribe /path/to/audio/folder -o my_transcriptions.xlsx

# Local API server
uv run audio-transcriber server
uv run audio-transcriber server --host 0.0.0.0 --port 8000 --reload

# Compatibility: works without subcommand
uv run audio-transcriber /path/to/audio/folder -o result.xlsx
```

### 2️⃣ REST API

```bash
# Start server (recommended)
uv run audio-transcriber server

# Or directly with uvicorn
uv run uvicorn audio_transcriber.api.main:app --reload
```

**Available endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive documentation (Swagger)
- `POST /transcribe` - Transcribe single file
- `POST /transcribe/batch` - Transcribe multiple files
- `POST /transcribe/download` - Transcribe and download result

### 3️⃣ Docker

#### Quick Start - REST API
```bash
# Using docker-compose (recommended - auto loads .env)
docker compose up

# Access API at: http://localhost:8001 (or your configured DOCKER_PORT)
```

#### Quick Start - MCP Server
```bash
# Start MCP HTTP server for remote AI agents (VPS deployment)
docker compose --profile mcp up

# Or start MCP STDIO server for local AI agents
docker compose --profile mcp-stdio up audio-transcriber-mcp

# Or start both API and MCP HTTP
docker compose --profile mcp up
```

#### Manual Docker Commands
```bash
# Build image
docker build -t audio-transcriber .

# Run REST API
docker run -p 8001:8001 -e OPENAI_API_KEY=your_key audio-transcriber

# Run MCP Server
docker run -it --env-file .env audio-transcriber uv run audio-transcriber-mcp
```

#### 🔧 Docker Configuration

Docker configuration is done through the `.env` file:

```bash
# Docker exposed port (maps to host)
DOCKER_PORT=8001

# MCP Server Docker port (for AI agents)
MCP_DOCKER_PORT=8002

# MCP Server HTTP settings (for remote access)
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8003

# Other variables are automatically loaded
OPENAI_API_KEY=your_key_here
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=25
```

**Available Services:**

| Service | Purpose | Use Case | Command | Access |
|---------|---------|----------|---------|--------|
| `audio-transcriber-api` | REST API Server | Web endpoints | `docker compose up` | `:${DOCKER_PORT}` |
| `audio-transcriber-mcp-http` | MCP HTTP Server | Remote AI agents, VPS | `docker compose --profile mcp up` | `:${MCP_SERVER_PORT}` |
| `audio-transcriber-mcp` | MCP STDIO Server | Local Claude Desktop | `docker compose --profile mcp-stdio up` | stdio |
| `nginx` | Reverse Proxy | Production deployment | `docker compose --profile production up` | `:80/:443` |

**docker-compose.yml features:**
- ✅ **Auto .env loading**: Automatically loads `.env` 
- ✅ **Configurable ports**: Uses `DOCKER_PORT` and `MCP_DOCKER_PORT` from .env
- ✅ **Health checks**: Built-in health monitoring (API only)
- ✅ **Non-root execution**: Secure container execution
- ✅ **Multi-service**: Supports both REST API and MCP Server
- ✅ **Profile-based**: Optional services via profiles
- ✅ **Custom networking**: Isolated internal communication

> **📋 For detailed Docker + MCP setup, see [DOCKER-MCP.md](DOCKER-MCP.md)**

#### ⚠️ Important: Build Requirements

When changing Docker-related variables in `.env`, you **MUST rebuild** the image:

```bash
# Variables that require rebuild:
# - DOCKER_PORT (used as build argument for API)
# - MCP_DOCKER_PORT (used as build argument for MCP Server)
# - Any configuration affecting the Docker image

# Rebuild after changing these variables:
docker compose build
docker compose up
```

**Why rebuild is needed:**
- `DOCKER_PORT` is passed as build argument (`APP_PORT`) for REST API
- `MCP_DOCKER_PORT` is passed as build argument for MCP Server
- `EXPOSE` directive is "baked" into the image
- Container startup command uses the build-time port

#### 🐳 Docker Production Deploy
```bash
# Build and tag for production
docker build -t your-registry/audio-transcriber:latest .
docker push your-registry/audio-transcriber:latest

# Deploy with docker-compose
docker compose -f docker-compose.yml up -d
```

### 4️⃣ AWS Lambda

```bash
# Deploy using SAM CLI
cd aws
./deploy.sh

# Or manually
sam build
sam deploy --guided
```

### 5️⃣ MCP Server (Model Context Protocol)

For integration with AI agents and messaging applications like WhatsApp:

```bash
# MCP HTTP Server (for VPS/remote deployment)
uv run audio-transcriber-mcp-http

# MCP STDIO Server (for local Claude Desktop)
uv run audio-transcriber-mcp

# Configure in MCP client (e.g., Claude Desktop or Anthropic MCP Connector)
# See MCP-SERVER.md for complete configuration
```

**Available MCP tools:**
- `transcribe_audio`: Single file transcription from URL
- `transcribe_batch`: Batch processing (up to 10 files)
- `get_server_status`: Health check and status
- `list_supported_formats`: Available audio formats

**MCP Deployment Options:**
- **HTTP Mode** (Port 8003): For VPS deployment, Portainer/Docker, or remote AI agents
- **STDIO Mode**: For local Claude Desktop integration only

**When to use each mode:**
- **Use HTTP Mode** for: VPS deployment, WhatsApp integration, remote AI agents, production environments
- **Use STDIO Mode** for: Local development with Claude Desktop

**HTTP Mode Configuration (.env):**
```bash
# MCP HTTP Server settings (required for remote access)
MCP_SERVER_HOST=0.0.0.0    # Allow external connections
MCP_SERVER_PORT=8003       # HTTP port for MCP protocol
```

**Example usage via MCP:**
```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "audio_url": "https://media.whatsapp.com/voice/abc123.ogg",
    "language": "pt"
  }
}
```

### 6️⃣ Programatically

```python
# Standard use (local)
from audio_transcriber import AudioTranscriber

transcriber = AudioTranscriber()
excel_file = transcriber.process_folder("/path/to/audios")

# As a service (API)
from audio_transcriber.api import TranscriptionService

service = TranscriptionService()
result = await service.transcribe_single_file(
    file_content=audio_bytes,
    filename="audio.mp3",
    output_format="json"
)
```

> **💡 Tip:** To use into Python scripts, execute with `uv run python my_script.py` to ensure that the correct virtual environment is in use.

## 📊 Results

The tool generates an Excel file with two sheets:

### "Transcription" Sheet
- **ID**: Sequential numbering
- **Filename**: Original audio name
- **Transcription**: Transcribed text
- **Success**: Whether transcription was successful
- **Error**: Error details (if any)
- **Size (MB)**: File size
- **Processing time**: Time spent on transcription
- **Transcription date**: When it was processed
- **Modification date**: Original file date
- **Full path**: File location

### "Summary" Sheet
- Total files processed
- Successful transcriptions
- Number of failures
- Success rate
- Total size processed
- Total processing time
- Processing date

## 🔧 Supported Formats

The tool supports all formats accepted by OpenAI API:

- **MP3** (.mp3)
- **MP4** (.mp4)
- **MPEG** (.mpeg)
- **MPGA** (.mpga)
- **M4A** (.m4a)
- **WAV** (.wav)
- **WebM** (.webm)
- **OGG** (.ogg)
- **FLAC** (.flac)

## ⚠️ Limitations

- **Maximum size**: 25MB per file (OpenAI limitation)
- **Rate limiting**: There's a 0.5s pause between requests to avoid overload
- **Cost**: Each transcription consumes credits from your OpenAI account

## 🛠️ Project Structure

```
audio-transcriber/
├── src/
│   └── audio_transcriber/
│       ├── __init__.py           # Main module
│       ├── cli.py               # Command line interface
│       ├── core/                # Main logic
│       │   ├── __init__.py
│       │   ├── config.py        # Configuration management
│       │   └── transcriber.py   # AudioTranscriber class
│       ├── api/                 # API REST
│       │   ├── __init__.py
│       │   ├── main.py          # FastAPI app
│       │   ├── models.py        # Pydantic models
│       │   └── service.py       # Transcription services
│       └── mcp/                 # MCP Server
│           ├── __init__.py
│           ├── server.py        # MCP Server implementation
│           ├── service.py       # MCP-specific services
│           └── models.py        # MCP data models
├── tests/                       # Unit tests
├── examples/                    # Usage examples
├── scripts/                     # Utilitary scripts
│   ├── setup_env.py            # .env configuration
│   ├── test_env.py             # configuration test
│   ├── test_api.py             # API test
│   └── test_setup.py           # Full verification
├── aws/                         # Deploy AWS Lambda
│   ├── template.yaml           # SAM template
│   ├── deploy.sh               # Deploy script
│   └── lambda_handler.py       # Handler Lambda
├── mcp-config.json             # MCP Server configuration example
├── MCP-SERVER.md               # MCP Server documentation
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml          # Docker Compose configuration
├── .env.example                # Configuration example
├── .env                       # Your configuration (dot not commit)
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🧪 Tests & Development

```bash
# Execute unit tests
uv run pytest

# Configuration test
uv run python scripts/test_env.py

# API test (server should be running)
uv run python scripts/test_api.py

# Code formatting
uv run black src tests examples
uv run isort src tests examples

# Types verification
uv run mypy src

# All the checks
uv run pytest && uv run black --check src && uv run isort --check src && uv run mypy src
```

## � Production Deploy

### Docker
```bash
# Build and push to registry
docker build -t seu-registry/audio-transcriber:latest .
docker push seu-registry/audio-transcriber:latest

# Deploy with docker-compose
docker compose -f docker-compose.yml up -d
```

### AWS Lambda
```bash
# Pre-requirements: Configured AWS CLI & Installed SAM CLI
cd aws
./deploy.sh

# Or manual deploy
sam build
sam deploy --guided --parameter-overrides OpenAIApiKey=sua_chave
```

## 🔍 Usage examples

```python
 # Full example
 # Execute with: uv run python my_script.py
from audio_transcriber import AudioTranscriber

# Configure transcriber
transcriber = AudioTranscriber()

# Process an audios folder
folder = "/home/user/my_audios"
excel_file = transcriber.process_folder(
    folder_path=folder,
    output_file="transcriptions.xlsx"
)

print(f"Transcriptions saved into: {excel_file}")
```

> **💡 Tip:** To execute Python scripts that use Audio Transcriber, always use `uv run python my_script.py` to ensure that all dependencies are available.

## 📝 Activities logs

This tool generates detailed logs showing:
- Files found
- Process progress
- Success & fails
- Process time
- Summary

## 🆘 Troubleshooting

### Error: "OpenAI key not found"
- Configure the environment variable `OPENAI_API_KEY`
- Or pass the key as parameter

### Error: "Folder not found"
- Check if the path is correct
- Use absolute paths when possible

### Error: "No audio files found"
- Confirm there are audio files in the folder
- Check if formats are supported

### Error: "File too large"
- File exceeds 25MB (OpenAI limit)
- Consider compressing or splitting the file

## 💡 Tips

1. **Organize your audios** in a specific folder
2. **Use descriptive names** for files
3. **Monitor costs** of OpenAI API
4. **Backup** important transcriptions
5. **Test with few files** first
6. **Use `uv run`** whenever executing Python commands
7. **Configure .env** once and reuse configurations
8. **Use SERVER_RELOAD=true** only in development
9. **For production** configure SERVER_HOST=0.0.0.0 and use multiple workers

### 🚀 Most Used Commands
```bash
# Check configurations
uv run python scripts/test_config.py

# Development server (with .env)
uv run audio-transcriber server

# Production server (temporary override)
uv run audio-transcriber server --host 0.0.0.0 --port 80 --workers 4

# Docker development (auto loads .env)
docker compose up

# Docker rebuild (after changing DOCKER_PORT)
docker compose build && docker compose up

# Local transcription
uv run audio-transcriber transcribe ./my_audios -o result.xlsx

# MCP Server HTTP (for VPS/remote AI agents)
uv run audio-transcriber-mcp-http

# MCP Server STDIO (for local Claude Desktop)
uv run audio-transcriber-mcp

# Quick API test
uv run python scripts/test_api.py
```

## 📄 License

This project is provided as is, for educational and professional use.

---

🔗 **Need help?** Check error logs or get in touch!
