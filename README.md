# 🎵 Audio Transcriber

**Professional audio transcription tool using OpenAI Whisper**

Complete solution with multiple deployment options:
- **📱 CLI** - Command line interface for batch processing
- **🌐 REST API** - FastAPI web server with automatic documentation  
- **🔗 MCP Server** - Model Context Protocol for AI agents integration
- **🐳 Docker** - Containerized deployment
- **☁️ AWS Lambda** - Serverless cloud deployment

## ⚡ Quick Start

### 1. Installation
```bash
# Install uv (Python dependency manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repository_url>
cd audio-transcriber
uv sync
```

### 2. Configuration
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 3. Usage

**CLI (Batch Processing)**
```bash
uv run audio-transcriber transcribe ./audios -o result.xlsx
```

**REST API Server**
```bash
uv run audio-transcriber server
# Access: http://localhost:8000/docs
```

**MCP Server (AI Agents)**
```bash
uv run audio-transcriber-mcp
# For HTTP version: uv run audio-transcriber-mcp-http
```

## 📁 Project Structure

```
├── src/audio_transcriber/     # Core application
│   ├── core/                  # Business logic
│   ├── api/                   # REST API (FastAPI)
│   ├── mcp/                   # MCP Server for AI agents
│   └── cli.py                 # Command line interface
├── docker-compose.yml         # Local development
├── docker-compose.portainer.yml # Production deployment
├── aws/                       # AWS Lambda deployment
└── docs/                      # Additional documentation
```

## 🚀 Deployment Options

### Local Development
```bash
# Direct CLI
uv run audio-transcriber transcribe ./audios

# Development server with auto-reload
uv run audio-transcriber server --reload
```

### Docker (Development)
```bash
docker compose up
# API: http://localhost:8001
```

### Production (VPS + Portainer)
See detailed instructions: **[PORTAINER.md](PORTAINER.md)**
- Traefik integration with SSL
- Environment variables configuration
- Health monitoring

### AWS Lambda (Serverless)
See detailed instructions: **[aws/README.md](aws/README.md)**
- SAM deployment
- API Gateway integration
- S3 bucket configuration

### MCP Server for AI Agents
See detailed instructions: **[MCP-SERVER.md](MCP-SERVER.md)**
- WhatsApp integration
- URL-based transcription
- AI agent protocols

## 📖 API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional
AUTH_TOKEN=your-bearer-token         # API protection
SERVER_HOST=0.0.0.0                 # Server host
SERVER_PORT=8000                    # Server port
LOG_LEVEL=INFO                      # Logging level
MAX_FILE_SIZE_MB=25                 # File size limit
```

### Supported Formats
- **Input**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, OGG, FLAC
- **Output**: JSON, TXT, Excel (XLSX), CSV
- **Languages**: Auto-detect or specify (pt, en, es, fr, de, etc.)

## 🛠️ Development

### Testing
```bash
# Run all tests
uv run pytest

# Test configuration
uv run python scripts/test_config_validation.py

# Test API integration
uv run python scripts/test_final_validation.sh
```

### Building
```bash
# Build package
uv build

# Build Docker image
docker build -t audio-transcriber .
```

## 📚 Detailed Documentation

For specific deployment scenarios and advanced configurations:

- **[PORTAINER.md](PORTAINER.md)** - VPS deployment with Portainer and Traefik
- **[MCP-SERVER.md](MCP-SERVER.md)** - AI agents integration and MCP protocol
- **[aws/README.md](aws/README.md)** - AWS Lambda serverless deployment
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Development guide

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

**Need help?** Check the specific documentation files above or open an issue.
