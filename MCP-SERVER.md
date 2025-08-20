# Audio Transcriber MCP Server

## Overview

The Audio Transcriber MCP Server is a server that implements the Model Context Protocol (MCP) to provide audio transcription capabilities using OpenAI's Whisper model. This server is especially useful for integration with messaging applications like WhatsApp, allowing AIs to transcribe voice messages automatically.

## Key Features

- **Single file transcription**: Transcription of an audio file from a URL
- **Batch transcription**: Processing multiple files simultaneously
- **URL support**: Accepts audio file URLs (ideal for WhatsApp and other platforms)
- **Multiple formats**: MP3, WAV, OGG, M4A, FLAC, WebM, MP4, MPEG, MPGA
- **Language detection**: Manual or automatic language detection support
- **File validation**: Size and format verification before processing

## Deployment Modes

The Audio Transcriber MCP Server supports two deployment modes:

### STDIO Mode (Local Integration)
- **Purpose**: Local integration with Claude Desktop and MCP clients
- **Transport**: JSON-RPC over stdin/stdout
- **Use Cases**: Development, local AI assistants, Claude Desktop integration
- **Command**: `uv run audio-transcriber-mcp`

### HTTP Mode (Remote Integration)
- **Purpose**: Remote deployment for VPS, Docker, and remote AI agents
- **Transport**: HTTP REST API with MCP-compatible endpoints
- **Use Cases**: VPS deployment, WhatsApp integration, remote AI agents, production environments
- **Command**: `uv run audio-transcriber-mcp-http`
- **Default Port**: 8003 (configurable via `MCP_SERVER_PORT`)

### When to Use Each Mode

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| Claude Desktop integration | STDIO | Direct process communication |
| Local development/testing | STDIO | Simpler setup, no network required |
| VPS deployment with Portainer | HTTP | Remote access, container orchestration |
| WhatsApp bot integration | HTTP | Web-accessible endpoint for webhooks |
| Production AI agent deployment | HTTP | Scalable, network-accessible |
| Multiple remote clients | HTTP | Concurrent access support |

## Installation and Configuration

### 1. Configure Dependencies

```bash
# Install MCP dependencies
uv add mcp httpx

# Verify installation
uv run audio-transcriber-mcp --help
```

### 2. Configure OpenAI Key

```bash
# Configure in .env
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> .env

# Or via environment variable
export OPENAI_API_KEY="sk-proj-your-key-here"
```

### 3. MCP Client Configuration

#### STDIO Mode (Local Claude Desktop)

Add to your MCP client configuration file (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "audio-transcriber": {
      "command": "uv",
      "args": ["run", "audio-transcriber-mcp"],
      "cwd": "/path/to/audio-transcriber",
      "env": {
        "OPENAI_API_KEY": "sk-proj-your-key-here"
      }
    }
  }
}
```

#### HTTP Mode (VPS/Remote Deployment)

For HTTP mode, configure the server settings in `.env`:

```bash
# MCP HTTP Server Configuration
MCP_SERVER_HOST=0.0.0.0      # Allow external connections
MCP_SERVER_PORT=8003         # HTTP port for MCP protocol
OPENAI_API_KEY=sk-proj-your-key-here
```

Start the HTTP server:
```bash
# Direct execution
uv run audio-transcriber-mcp-http

# Docker deployment
docker compose --profile mcp up

# Or via Docker with custom port mapping
docker run -p 8003:8003 --env-file .env audio-transcriber uv run audio-transcriber-mcp-http
```

Configure your MCP client to connect via HTTP (example for Anthropic MCP Connector):
```json
{
  "servers": {
    "audio-transcriber": {
      "url": "http://your-vps-ip:8003",
      "headers": {
        "Authorization": "Bearer your-auth-token"
      }
    }
  }
}
```

## Available Tools

### 1. `transcribe_audio`

Transcribes a single audio file from a URL.

**Parameters:**
- `audio_url` (required): Audio file URL
- `language` (optional): ISO-639-1 language code (e.g., 'pt', 'en', 'es')
- `max_file_size_mb` (optional, default: 25): Maximum file size in MB
- `timeout_seconds` (optional, default: 300): Timeout in seconds

**Example:**
```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "audio_url": "https://example.com/audio.mp3",
    "language": "pt",
    "max_file_size_mb": 20
  }
}
```

### 2. `transcribe_batch`

Transcribes multiple audio files in batch.

**Parameters:**
- `audio_urls` (required): List of URLs (maximum 10)
- `language` (optional): Language for all files
- `max_file_size_mb` (optional, default: 25): Maximum size per file
- `timeout_seconds` (optional, default: 300): Timeout per file

**Example:**
```json
{
  "tool": "transcribe_batch",
  "arguments": {
    "audio_urls": [
      "https://example.com/audio1.mp3",
      "https://example.com/audio2.wav"
    ],
    "language": "en"
  }
}
```

### 3. `get_server_status`

Checks server status and health.

**Example:**
```json
{
  "tool": "get_server_status",
  "arguments": {}
}
```

### 4. `list_supported_formats`

Lists all supported audio formats.

**Example:**
```json
{
  "tool": "list_supported_formats",
  "arguments": {}
}
```

## WhatsApp Integration

To integrate with WhatsApp or other messaging platforms, you typically receive audio file URLs:

```json
{
  "tool": "transcribe_audio",
  "arguments": {
    "audio_url": "https://media.whatsapp.com/voice/abc123.ogg",
    "language": "pt",
    "timeout_seconds": 120
  }
}
```

## Response Format

All tools return structured JSON responses (MCP protocol standard):

```json
{
  "success": true,
  "transcription": "Hello, this is the audio transcription.",
  "filename": "audio.mp3",
  "file_size_mb": 2.5,
  "processing_time_seconds": 3.2,
  "language_specified": "pt",
  "audio_url": "https://example.com/audio.mp3",
  "audio_format": ".mp3",
  "download_time_seconds": 1.1,
  "timestamp": "2025-08-20T10:30:00",
  "model_used": "whisper-1",
  "error": null
}
```

> **Note**: Unlike the REST API which supports multiple output formats (JSON, Excel, CSV, TXT), the MCP Server always returns JSON responses as required by the MCP protocol specification.
```

## Error Handling

The server returns structured errors in case of failure:

```json
{
  "success": false,
  "transcription": "",
  "filename": "audio.mp3",
  "error": "File too large (30MB, max: 25MB)",
  "timestamp": "2025-08-20T10:30:00"
}
```

## Limitations and Considerations

- **Maximum size**: 25MB per file (OpenAI limitation)
- **Rate limiting**: 0.5 seconds between requests to avoid overload
- **Timeout**: Maximum 15 minutes per request
- **Supported formats**: Limited to formats accepted by OpenAI API
- **Network dependency**: Requires stable connection for file downloads

## Testing and Development

### Test the MCP Server

```bash
# Check if server starts correctly
uv run audio-transcriber-mcp

# Test with an MCP client
# (server will wait for connections via stdio)
```

### Logs and Debug

The server logs useful information for debugging:

```bash
# Run with detailed logs
LOG_LEVEL=DEBUG uv run audio-transcriber-mcp
```

## Security

- **API keys**: Never expose your OpenAI key in logs or versioned configuration files
- **Input URLs**: The server validates URLs but doesn't implement authentication
- **Temporary files**: Downloaded files are automatically removed after processing
- **Rate limiting**: Implemented to avoid OpenAI API overload

## Use Cases

1. **WhatsApp Bot**: Transcribe received voice messages
2. **AI Assistants**: Process audio sent by users
3. **Automation Systems**: Transcribe audio files in pipelines
4. **Content Analysis**: Process multiple audio files for analysis
5. **Accessibility**: Convert audio to text for hearing-impaired users

## MCP vs REST API Comparison

The Audio Transcriber provides both MCP and REST API interfaces. Here are the key differences:

| Feature | MCP STDIO | MCP HTTP | REST API |
|---------|-----------|----------|----------|
| **Input Method** | URLs only | URLs only | File uploads + URLs |
| **Output Format** | JSON only | JSON only | JSON, Excel, CSV, TXT |
| **Target Audience** | Local AI agents | Remote AI agents | Web applications, direct usage |
| **Protocol** | JSON-RPC over stdio | HTTP with MCP endpoints | HTTP REST |
| **Authentication** | Environment-based | HTTP headers/tokens | HTTP headers/tokens |
| **Batch Processing** | Up to 10 files | Up to 10 files | Unlimited |
| **Deployment** | Local only | Network accessible | Network accessible |
| **Use Cases** | Claude Desktop, local bots | VPS, WhatsApp bots, remote AI | Web apps, manual processing |

### Deployment Recommendations

| Scenario | Recommended Option | Reason |
|----------|-------------------|--------|
| **Local Claude Desktop** | MCP STDIO | Direct integration, no network setup |
| **VPS with Portainer** | MCP HTTP | Remote access, container orchestration |
| **WhatsApp Integration** | MCP HTTP or REST API | Web-accessible endpoints |
| **Web Application** | REST API | Full feature set, multiple formats |
| **Development/Testing** | MCP STDIO | Simple setup, quick testing |
| **Production AI Agents** | MCP HTTP | Scalable, concurrent access |

> **When to use MCP STDIO**: Local development, Claude Desktop integration
> 
> **When to use MCP HTTP**: VPS deployment, remote AI agents, production environments
> 
> **When to use REST API**: Web applications, manual processing, need for multiple output formats

## Additional Resources

The MCP server also provides informational resources:

- `info://audio-transcriber/about`: General information about the server
- `info://audio-transcriber/formats`: Details about supported formats
- `info://audio-transcriber/examples`: Usage examples

These resources can be accessed by MCP clients to get contextual documentation.
