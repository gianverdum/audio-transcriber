"""
MCP (Model Context Protocol) Server for Audio Transcriber
Provides audio transcription tools for AI agents via MCP protocol
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    Resource,
    ListResourcesRequest,
    ListResourcesResult,
)

from .service import MCPTranscriptionService
from .models import (
    TranscribeAudioInput,
    BatchTranscribeInput,
    ServerStatusOutput,
    MCPError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP Server instance
app = Server("audio-transcriber")

# Initialize transcription service
transcription_service: Optional[MCPTranscriptionService] = None


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for audio transcription"""
    return [
        Tool(
            name="transcribe_audio",
            description="Transcribe audio from URL using OpenAI Whisper",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL of the audio file to transcribe"
                    },
                    "language": {
                        "type": "string",
                        "pattern": "^[a-z]{2}$",
                        "description": "Audio language in ISO-639-1 format (e.g., 'pt', 'en', 'es')"
                    },
                    "max_file_size_mb": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25,
                        "description": "Maximum file size in MB"
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "minimum": 30,
                        "maximum": 900,
                        "default": 300,
                        "description": "Timeout for transcription in seconds"
                    }
                },
                "required": ["audio_url"]
            }
        ),
        Tool(
            name="transcribe_batch",
            description="Transcribe multiple audio files from URLs in batch",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_urls": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "uri"
                        },
                        "minItems": 1,
                        "maxItems": 10,
                        "description": "List of audio URLs to transcribe (max 10)"
                    },
                    "language": {
                        "type": "string",
                        "pattern": "^[a-z]{2}$",
                        "description": "Audio language in ISO-639-1 format (applies to all files)"
                    },
                    "max_file_size_mb": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25,
                        "description": "Maximum file size in MB per file"
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "minimum": 30,
                        "maximum": 900,
                        "default": 300,
                        "description": "Timeout per file in seconds"
                    }
                },
                "required": ["audio_urls"]
            }
        ),
        Tool(
            name="get_server_status",
            description="Get server status and health information",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="list_supported_formats",
            description="List all supported audio formats",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    global transcription_service
    
    if transcription_service is None:
        transcription_service = MCPTranscriptionService()
    
    try:
        if name == "transcribe_audio":
            # Validate and parse input
            try:
                input_data = TranscribeAudioInput(**arguments)
            except Exception as e:
                error = MCPError(
                    error_type="ValidationError",
                    message=f"Invalid input parameters: {str(e)}",
                    timestamp=datetime.now()
                )
                return [TextContent(type="text", text=json.dumps(error.dict(), default=str))]
            
            # Perform transcription
            result = await transcription_service.transcribe_audio_from_url(input_data)
            return [TextContent(type="text", text=json.dumps(result.dict(), default=str))]
            
        elif name == "transcribe_batch":
            # Validate and parse input
            try:
                input_data = BatchTranscribeInput(**arguments)
            except Exception as e:
                error = MCPError(
                    error_type="ValidationError",
                    message=f"Invalid input parameters: {str(e)}",
                    timestamp=datetime.now()
                )
                return [TextContent(type="text", text=json.dumps(error.dict(), default=str))]
            
            # Perform batch transcription
            result = await transcription_service.transcribe_batch_from_urls(input_data)
            return [TextContent(type="text", text=json.dumps(result.dict(), default=str))]
            
        elif name == "get_server_status":
            # Get server status
            result = await transcription_service.get_server_status()
            return [TextContent(type="text", text=json.dumps(result.dict(), default=str))]
            
        elif name == "list_supported_formats":
            # List supported formats
            formats = {
                "supported_formats": list(transcription_service.supported_formats),
                "format_descriptions": {
                    ".mp3": "MPEG Audio Layer III",
                    ".mp4": "MPEG-4 Audio",
                    ".mpeg": "MPEG Audio",
                    ".mpga": "MPEG Audio",
                    ".m4a": "MPEG-4 Audio",
                    ".wav": "Waveform Audio File Format",
                    ".webm": "WebM Audio",
                    ".ogg": "Ogg Vorbis",
                    ".flac": "Free Lossless Audio Codec"
                },
                "max_file_size_mb": 25,
                "note": "All formats are processed by OpenAI's Whisper model"
            }
            return [TextContent(type="text", text=json.dumps(formats, indent=2))]
            
        else:
            error = MCPError(
                error_type="UnknownTool",
                message=f"Unknown tool: {name}",
                timestamp=datetime.now()
            )
            return [TextContent(type="text", text=json.dumps(error.dict(), default=str))]
            
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        error = MCPError(
            error_type="InternalError",
            message=f"Internal server error: {str(e)}",
            timestamp=datetime.now()
        )
        return [TextContent(type="text", text=json.dumps(error.dict(), default=str))]


@app.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="info://audio-transcriber/about",
            name="Audio Transcriber Information",
            description="Information about the Audio Transcriber MCP Server",
            mimeType="text/plain"
        ),
        Resource(
            uri="info://audio-transcriber/formats",
            name="Supported Audio Formats",
            description="List of supported audio formats and their specifications",
            mimeType="application/json"
        ),
        Resource(
            uri="info://audio-transcriber/examples",
            name="Usage Examples",
            description="Examples of how to use the audio transcription tools",
            mimeType="text/markdown"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "info://audio-transcriber/about":
        return """
# Audio Transcriber MCP Server

This MCP server provides audio transcription capabilities using OpenAI's Whisper model.

## Features:
- Transcribe audio files from URLs
- Support for multiple audio formats (MP3, WAV, OGG, etc.)
- Batch processing of multiple files
- Automatic language detection or manual language specification
- Integration with messaging platforms like WhatsApp

## Configuration:
- Requires OPENAI_API_KEY environment variable
- Maximum file size: 25MB (OpenAI limitation)
- Supported languages: All languages supported by Whisper

## Use Cases:
- WhatsApp voice message transcription
- Audio content processing for AI agents
- Automated transcription workflows
- Multi-language audio processing
        """
    
    elif uri == "info://audio-transcriber/formats":
        formats_info = {
            "supported_formats": [
                {
                    "extension": ".mp3",
                    "name": "MPEG Audio Layer III",
                    "recommended": True,
                    "quality": "Good compression with acceptable quality loss"
                },
                {
                    "extension": ".wav",
                    "name": "Waveform Audio File Format",
                    "recommended": True,
                    "quality": "Lossless, high quality but larger files"
                },
                {
                    "extension": ".ogg",
                    "name": "Ogg Vorbis",
                    "recommended": True,
                    "quality": "Good compression with better quality than MP3"
                },
                {
                    "extension": ".m4a",
                    "name": "MPEG-4 Audio",
                    "recommended": True,
                    "quality": "Good compression, common on Apple devices"
                },
                {
                    "extension": ".flac",
                    "name": "Free Lossless Audio Codec",
                    "recommended": False,
                    "quality": "Lossless but very large files"
                },
                {
                    "extension": ".webm",
                    "name": "WebM Audio",
                    "recommended": False,
                    "quality": "Web-optimized format"
                }
            ],
            "limitations": {
                "max_file_size_mb": 25,
                "timeout_seconds": 900,
                "rate_limiting": "0.5 seconds between requests"
            },
            "language_codes": {
                "pt": "Portuguese",
                "en": "English",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "it": "Italian",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese",
                "ru": "Russian"
            }
        }
        return json.dumps(formats_info, indent=2)
    
    elif uri == "info://audio-transcriber/examples":
        return """
# Audio Transcriber Usage Examples

## Single File Transcription

```json
{
    "tool": "transcribe_audio",
    "arguments": {
        "audio_url": "https://example.com/audio.mp3",
        "language": "pt"
    }
}
```

## Batch Transcription

```json
{
    "tool": "transcribe_batch",
    "arguments": {
        "audio_urls": [
            "https://example.com/audio1.mp3",
            "https://example.com/audio2.wav"
        ],
        "language": "en",
        "max_file_size_mb": 20
    }
}
```

## WhatsApp Integration Example

For WhatsApp voice messages, you typically receive a URL to the audio file:

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

## Server Status Check

```json
{
    "tool": "get_server_status",
    "arguments": {}
}
```

## Response Format

All tools return JSON responses with detailed information:

```json
{
    "success": true,
    "transcription": "Hello, this is the transcribed text.",
    "filename": "audio.mp3",
    "file_size_mb": 2.5,
    "processing_time_seconds": 3.2,
    "language_specified": "en",
    "audio_url": "https://example.com/audio.mp3",
    "timestamp": "2025-08-20T10:30:00"
}
```
        """
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Audio Transcriber MCP Server...")
    
    # Validate OpenAI API key
    from ..core.config import settings
    if not settings.validate_openai_key():
        logger.error("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
        return
    
    logger.info("OpenAI API key configured successfully")
    logger.info("Available tools: transcribe_audio, transcribe_batch, get_server_status, list_supported_formats")
    logger.info("Server ready for MCP connections")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, 
                     app.create_initialization_options())


def main_sync():
    """Synchronous entry point for the MCP server"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
