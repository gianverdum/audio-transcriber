# Docker Configuration for MCP Server

This document explains how to run both REST API and MCP Server using Docker.

## Quick Start

### Run REST API Server (default)
```bash
# Start REST API server
docker compose up audio-transcriber-api

# Access at http://localhost:8000
```

### Run MCP Server
```bash
# Start MCP Server for AI agents
docker compose --profile mcp up audio-transcriber-mcp

# Connect via stdio for MCP communication
```

### Run Both Services
```bash
# Start both API and MCP servers
docker compose --profile mcp up
```

## Configuration

### Environment Variables

Both services use the same `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=25
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
DOCKER_PORT=8001
MCP_DOCKER_PORT=8002  # MCP Server Docker build port
```

### Service Definitions

#### `audio-transcriber-api`
- **Purpose**: REST API server for web applications
- **Port**: `${DOCKER_PORT:-8000}` (configurable)
- **Health check**: `/health` endpoint
- **Usage**: Direct HTTP requests

#### `audio-transcriber-mcp`
- **Purpose**: MCP server for AI agents
- **Communication**: stdio (no exposed ports)
- **Build Port**: Uses `${MCP_DOCKER_PORT:-8002}` for build argument only
- **Profile**: `mcp` (optional service)
- **Usage**: AI agent integration

## Usage Examples

### 1. Development - REST API Only
```bash
# Start only the REST API
docker compose up audio-transcriber-api

# Test the API
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "language=pt"
```

### 2. AI Agent Integration - MCP Server
```bash
# Start MCP server
docker compose --profile mcp up audio-transcriber-mcp

# Connect from AI agent (example with Claude Desktop)
# See mcp-config-example.json for configuration
```

### 3. Production - Both Services
```bash
# Start all services including Nginx
docker compose --profile mcp --profile production up
```

## MCP Server Docker Details

### Dockerfile Modifications

The Dockerfile supports both modes:

```dockerfile
# Default: REST API server
CMD ["sh", "-c", "uv run audio-transcriber server --host 0.0.0.0 --port $APP_PORT"]

# Override for MCP: 
# docker run ... uv run audio-transcriber-mcp
```

### Docker Compose MCP Service

```yaml
audio-transcriber-mcp:
  # ... (build config same as API)
  command: ["uv", "run", "audio-transcriber-mcp"]
  stdin_open: true  # Required for stdio
  tty: true         # Required for stdio  
  profiles: ["mcp"] # Optional service
```

### Key Differences from API Service

| Feature | REST API Service | MCP Service |
|---------|------------------|-------------|
| **Ports** | Exposed (8001) | None (stdio) |
| **Health Check** | HTTP `/health` | None |
| **Communication** | HTTP requests | stdio/JSON-RPC |
| **Profile** | Default | `mcp` (optional) |
| **stdin/tty** | Not needed | Required |
| **Network** | Internal + External | Internal only |

## Docker Networking

### Internal Network Configuration

All services run on a custom Docker network:

```yaml
networks:
  audio-transcriber-network:
    driver: bridge
    name: audio-transcriber-net
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
```

### Benefits of Custom Network

- **🔒 Security**: Isolated network segment
- **📡 Internal Communication**: Services communicate by name
- **🛡️ Nginx Optimization**: Direct internal routing to API
- **📈 Scalability**: Easy to add more services
- **🔍 Monitoring**: Network-level observability

### Service Communication

```bash
# External access (from host)
curl http://localhost:8001/health

# Internal communication (nginx → api)
http://audio-transcriber-api:8001/health

# MCP Server (stdio only, no HTTP)
# Communicates via stdin/stdout
```

## Integration with AI Agents

### Claude Desktop Configuration

Create `~/.config/claude-desktop/config.json`:

```json
{
  "mcpServers": {
    "audio-transcriber": {
      "command": "docker",
      "args": [
        "compose", 
        "--profile", "mcp", 
        "exec", 
        "audio-transcriber-mcp",
        "uv", "run", "audio-transcriber-mcp"
      ],
      "cwd": "/path/to/audio-transcriber",
      "env": {
        "OPENAI_API_KEY": "sk-proj-your-key-here"
      }
    }
  }
}
```

### Alternative: Direct Docker Run

```bash
# Run MCP server directly
docker run -it \
  --env-file .env \
  --rm \
  audio-transcriber:latest \
  uv run audio-transcriber-mcp
```

## Troubleshooting

### MCP Server Issues

1. **"No stdio connection"**
   ```bash
   # Ensure stdin_open and tty are enabled
   docker compose logs audio-transcriber-mcp
   ```

2. **"OpenAI API key not found"**
   ```bash
   # Check environment file
   docker compose exec audio-transcriber-mcp env | grep OPENAI
   ```

3. **"Container exits immediately"**
   ```bash
   # Check if MCP dependencies are installed
   docker compose exec audio-transcriber-mcp uv run audio-transcriber-mcp --help
   ```

### API Server Issues

1. **"Port already in use"**
   ```bash
   # Change DOCKER_PORT in .env
   echo "DOCKER_PORT=8001" >> .env
   docker compose up --build
   ```

2. **"Health check failing"**
   ```bash
   # Check if server is running
   docker compose logs audio-transcriber-api
   curl http://localhost:8001/health
   ```

## Production Considerations

### Security
- Use secrets management for `OPENAI_API_KEY`
- Custom network provides container isolation
- Enable HTTPS with proper certificates (nginx profile)
- Firewall rules for external access only to necessary ports

### Networking
- **Internal communication**: Services use container names
- **External access**: Only API port (8001) exposed to host
- **MCP isolation**: No external ports, stdio communication only
- **Nginx proxy**: Routes traffic internally to `audio-transcriber-api:8001`

### Performance
- Limit container resources:
  ```yaml
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '0.5'
  ```

### Monitoring
- Add logging driver configuration
- Use health checks for both services
- Monitor MCP server via logs (no HTTP endpoints)

### Scaling
- REST API: Use multiple replicas behind load balancer
- MCP Server: One instance per AI agent (stdio is 1:1)

## Commands Reference

```bash
# Build and start API only
docker compose up --build audio-transcriber-api

# Build and start MCP only  
docker compose --profile mcp up --build audio-transcriber-mcp

# Start both services
docker compose --profile mcp up

# Rebuild after code changes
docker compose build && docker compose --profile mcp up

# View logs
docker compose logs audio-transcriber-mcp
docker compose logs audio-transcriber-api

# Access container shell
docker compose exec audio-transcriber-api bash
docker compose exec audio-transcriber-mcp bash

# Stop services
docker compose down
docker compose --profile mcp down
```

This configuration allows you to run both REST API and MCP Server efficiently using the same Docker image with different entry points.
