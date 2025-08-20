# Deploy on Portainer VPS

This guide expla4. **Environment variables**:
   ```
   OPENAI_API_KEY=sk-proj-your-openai-key-here
   AUTH_TOKEN=your-optional-bearer-token
   ```how to deploy Audio Transcriber on a VPS using Portainer and Traefik.

## 🚀 Prerequisites

### 1. Traefik configured on VPS
- Network `traefik_public` created
- Automatic SSL certificates (Let's Encrypt)
- Entrypoints `websecure` configured

### 2. DNS domains configured
- `audio-transcriber.api.bringideas.com.br` → VPS IP
- `audio-transcriber.mcp.bringideas.com.br` → VPS IP

### 3. Docker Secrets created in Portainer

## 🔐 Configuring Environment Variables in Portainer

### 1. Access Portainer
```
https://portainer.bringideas.com.br
```

### 2. Configure Environment Variables
1. Go to **Stacks** → **Add Stack** 
2. **Environment variables** section:
   ```
   OPENAI_API_KEY=sk-proj-your-openai-key-here
   AUTH_TOKEN=your-optional-bearer-token
   ```

**Note**: No Docker secrets needed! Everything is managed via environment variables in Portainer.

## 📦 Deploy via Portainer

### Option 1: Stack via Git Repository

1. **Go to Stacks** → **Add Stack**
2. **Method**: Repository
3. **Repository URL**: `https://github.com/gianverdum/audio-transcriber`
4. **Reference**: `feat/mcp-server` (or `main` after merge)
5. **Compose file path**: `docker-compose.portainer.yml`
6. **Environment variables**:
   ```
   AUTH_TOKEN=your-optional-bearer-token
   ```
7. **Deploy**

### Option 2: Stack via Upload

1. **Go to Stacks** → **Add Stack**
2. **Method**: Upload
3. Upload the file `docker-compose.portainer.yml`
4. **Environment variables**:
   ```
   OPENAI_API_KEY=sk-proj-your-openai-key-here
   AUTH_TOKEN=your-optional-bearer-token
   ```
5. **Deploy**

### Option 3: Stack via Web Editor

1. **Go to Stacks** → **Add Stack**
2. **Method**: Web editor
3. **Copy and paste** the contents of `docker-compose.portainer.yml`
4. **Environment variables**:
   ```
   OPENAI_API_KEY=sk-proj-your-openai-key-here
   AUTH_TOKEN=your-optional-bearer-token
   ```
5. **Deploy**

## 🌍 Available Endpoints

After successful deployment:

### REST API
- **URL**: `https://audio-transcriber.api.bringideas.com.br`
- **Docs**: `https://audio-transcriber.api.bringideas.com.br/docs`
- **Health**: `https://audio-transcriber.api.bringideas.com.br/health`

### MCP HTTP Server
- **URL**: `https://audio-transcriber.mcp.bringideas.com.br`
- **Health**: `https://audio-transcriber.mcp.bringideas.com.br/health`
- **Tools**: `transcribe_audio`, `transcribe_batch`, `get_server_status`, `list_supported_formats`

## 🔧 Testing the Deployment

### 1. Check Health Checks
```bash
# REST API
curl https://audio-transcriber.api.bringideas.com.br/health

# MCP HTTP
curl https://audio-transcriber.mcp.bringideas.com.br/health
```

### 2. Test Transcription (REST API)
```bash
curl -X POST "https://audio-transcriber.api.bringideas.com.br/transcribe" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -F "file=@audio.mp3" \
  -F "language=pt"
```

### 3. Test MCP Tools
```bash
curl -X POST "https://audio-transcriber.mcp.bringideas.com.br/mcp" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "transcribe_audio",
    "arguments": {
      "audio_url": "https://example.com/audio.mp3",
      "language": "pt"
    }
  }'
```

## 📊 Monitoring in Portainer

### 1. Container Logs
- **Containers** → Select container → **Logs**
- Check startup and health checks

### 2. Resource Usage
- **Containers** → **Stats**
- Monitor CPU, Memory, Network

### 3. Health Status
- Green: Healthy
- Yellow: Starting
- Red: Unhealthy

## 🛠️ Troubleshooting

### 1. Environment variables not found
```bash
# Check environment variables in Portainer
# Stack → Environment variables section

# Required variables:
OPENAI_API_KEY=sk-proj-...
AUTH_TOKEN=your-token (optional)
```

### 2. Health check failing
```bash
# Check container logs
docker service logs audio-transcriber_audio-transcriber-api

# Test health check manually
docker exec <container> curl -f http://localhost:8000/health
```

### 3. Traefik not routing
```bash
# Check Traefik labels
docker service inspect audio-transcriber_audio-transcriber-api

# Check traefik_public network
docker network inspect traefik_public
```

### 4. SSL/TLS Issues
```bash
# Check certificates
docker service logs traefik

# Check DNS resolution
nslookup audio-transcriber.api.bringideas.com.br
```

## 🔄 Updates

### 1. Update Image
1. **Stacks** → Select stack → **Editor**
2. Change image tag: `ghcr.io/gianverdum/audio-transcriber:latest`
3. **Update the stack**

### 2. Full Redeploy
1. **Stacks** → Select stack → **Down**
2. Wait for completion
3. **Up** again

## 📋 Important Configurations

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key (required)
- `AUTH_TOKEN` - Optional bearer token protection
- `SERVER_HOST=0.0.0.0` - Required for container networking
- `SERVER_PORT=8000` - Internal API port  
- `MCP_SERVER_PORT=8003` - Internal MCP port
- `LOG_LEVEL=INFO` - Logging level
- `MAX_FILE_SIZE_MB=25` - OpenAI file size limit

### Networks
- `traefik_public` - External network for Traefik
- `audio-transcriber-network` - Internal overlay network

### Secrets
- `openai_api_key` - OpenAI API key (required)

### Health Checks
- **Interval**: 15s
- **Timeout**: 5s  
- **Retries**: 5
- **Start Period**: 20s

---

🎯 **This setup provides a complete and production-ready solution for VPS with automatic SSL, monitoring, and high availability!**
