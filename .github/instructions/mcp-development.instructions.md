---
applyTo: '**'
---
# Audio Transcriber as an MCP Server

This guide explains how to expose the **audio-transcriber** project as an **MCP server** so that it can be used by an AI agent (e.g., via WhatsApp). The idea is to receive client audio files, transcribe them, and return text through the MCP protocol.

---

## 1. Overview

To make this project available as an MCP server:

1. **Choose a transport**  
   - **HTTP (recommended for production)**: works with Anthropic’s MCP Connector and remote agents.  
   - **STDIO (local development)**: good for testing with Claude Desktop or CLI.

2. **Add MCP SDK** to the project:  
   ```bash
   uv add mcp fastapi uvicorn
   ```
   or:
   ```bash
   pip install mcp fastapi uvicorn
   ```

3. **Wrap your transcription logic** as an MCP tool (`transcribe_audio`).

4. **Expose it** via HTTP (FastAPI + `FastMCP`) or STDIO.

5. **Secure and deploy** the service with authentication, size limits, and monitoring.

---

## 2. Minimal MCP Server (FastAPI + HTTP)

Create a file `mcp_server.py`:

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, HttpUrl
from typing import Optional

# 1) Base FastAPI app
app = FastAPI(title="Audio Transcriber MCP")

# 2) MCP instance integrated into FastAPI
mcp = FastMCP("audio-transcriber", stateless_http=True)

# 3) Input schema
class TranscribeInput(BaseModel):
    audio_url: HttpUrl
    language: Optional[str] = None
    diarize: bool = False

# 4) MCP tool
@mcp.tool()
def transcribe_audio(input: TranscribeInput) -> str:
    """
    Transcribes the audio at `audio_url` and returns the text.
    """
    # TODO: Replace this with your actual transcriber call
    # text = transcribe_from_url(input.audio_url, language=input.language, diarize=input.diarize)
    text = f"[demo] Transcribed {input.audio_url} (lang={input.language}, diarize={input.diarize})"
    return text

# 5) Mount MCP into the FastAPI app
mcp.mount(app)

# Run with:
# uvicorn mcp_server:app --host 0.0.0.0 --port 8080
```

---

## 3. WhatsApp Integration Flow

1. **Receive audio** via WhatsApp API (e.g., n8n + EvolutionAPI).  
   Save the file in a public storage bucket (S3, MinIO) and generate a temporary URL.  

2. **Call MCP tool**:  
   The agent (e.g., Anthropic via MCP Connector) calls the `transcribe_audio` tool, passing the `audio_url`.  

3. **Return transcription**:  
   The tool returns plain text, which the agent uses to reply to the client on WhatsApp.

---

## 4. Security & Production Checklist

- **Authentication**: Require a `Bearer` token header in FastAPI.  
- **File limits**: Enforce maximum file size (MB) and request timeout.  
- **Queueing**: For high load, offload transcription jobs to a queue (Celery, RQ).  
- **Observability**: Log tool calls, request duration, and audio size.  
- **MCP spec**: Track MCP spec versions (`YYYY-MM-DD`) to avoid breaking changes.

---

## 5. Choosing a Transport

- **STDIO (local dev)**:  
  - Simple to run locally.  
  - Works with Claude Desktop.  

- **HTTP (production)**:  
  - Required for Anthropic MCP Connector.  
  - Expose your FastAPI server publicly (with HTTPS and auth).  

---

## 6. Next Steps

1. Create a new branch:  
   ```bash
   git checkout -b feat/mcp-server
   ```

2. Add `mcp_server.py` and adapt it to call the real transcriber function.

3. Add a health check endpoint (`/health`) and auth middleware.

4. Deploy to a staging environment (Hetzner VPS, Railway, Fly.io, Render, etc.) with HTTPS.

5. Register the MCP endpoint with your AI agent (e.g., Anthropic MCP Connector) and test the `transcribe_audio` tool.

---
