"""
MCP (Model Context Protocol) HTTP Server for Audio Transcriber
HTTP-based MCP server for remote AI agent access via Anthropic MCP Connector
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP  # type: ignore[import-untyped]
from starlette.requests import Request
from starlette.responses import JSONResponse

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

# Initialize MCP service
mcp_service = MCPTranscriptionService()

# Create MCP server instance
mcp = FastMCP(
    name="audio-transcriber-mcp",
    instructions="Audio transcription server for AI agents. Transcribe audio files from URLs using OpenAI Whisper.",
    host="0.0.0.0",
    port=8003,
    stateless_http=True
)

# Add health check endpoint for Docker/Portainer
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint for Docker health checks and load balancers"""
    try:
        from audio_transcriber.core.config import settings
        has_api_key = settings.validate_openai_key()
        return JSONResponse({
            "status": "healthy" if has_api_key else "degraded",
            "timestamp": datetime.now().isoformat(),
            "service": "audio-transcriber-mcp-http",
            "version": "1.0.0",
            "openai_configured": has_api_key
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        })

@mcp.tool()
async def transcribe_audio(input_data: TranscribeAudioInput) -> Dict[str, Any]:
    """
    Transcribe a single audio file from URL.
    
    Args:
        input_data: Audio transcription input parameters
        
    Returns:
        Transcription result with metadata
    """
    try:
        logger.info(f"Transcribing audio from URL: {input_data.audio_url}")
        
        result = await mcp_service.transcribe_audio_from_url(
            url=str(input_data.audio_url),
            language=input_data.language,
            max_file_size_mb=input_data.max_file_size_mb,
            timeout_seconds=input_data.timeout_seconds
        )
        
        logger.info(f"Transcription completed successfully for {input_data.audio_url}")
        return result.model_dump()
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        error_result = MCPError(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            audio_url=str(input_data.audio_url)
        )
        return error_result.model_dump()

@mcp.tool()
async def transcribe_batch(input_data: BatchTranscribeInput) -> Dict[str, Any]:
    """
    Transcribe multiple audio files in batch.
    
    Args:
        input_data: Batch transcription input parameters
        
    Returns:
        Batch transcription results
    """
    try:
        logger.info(f"Transcribing batch of {len(input_data.audio_urls)} files")
        
        result = await mcp_service.transcribe_batch_from_urls(
            urls=[str(url) for url in input_data.audio_urls],
            language=input_data.language,
            max_file_size_mb=input_data.max_file_size_mb,
            timeout_seconds=input_data.timeout_seconds
        )
        
        logger.info(f"Batch transcription completed: {result.total_files} files")
        return result.model_dump()
        
    except Exception as e:
        logger.error(f"Error in batch transcription: {e}")
        error_result = MCPError(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            audio_url="batch_request"
        )
        return error_result.model_dump()

@mcp.tool()
async def get_server_status() -> Dict[str, Any]:
    """
    Get server status and health information.
    
    Returns:
        Server status information
    """
    try:
        result = await mcp_service.get_server_status()
        return result.model_dump()
    except Exception as e:
        logger.error(f"Error getting server status: {e}")
        error_result = MCPError(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            audio_url="status_check"
        )
        return error_result.model_dump()

@mcp.tool()
async def list_supported_formats() -> Dict[str, Any]:
    """
    List all supported audio formats.
    
    Returns:
        List of supported audio formats
    """
    try:
        formats = await mcp_service.list_supported_formats()
        return {
            "success": True,
            "supported_formats": formats,
            "total_formats": len(formats),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing formats: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main entry point for MCP HTTP server."""
    from audio_transcriber.core.config import settings
    
    # Update MCP server configuration from settings
    mcp.settings.host = settings.MCP_SERVER_HOST
    mcp.settings.port = settings.MCP_SERVER_PORT
    
    logger.info(f"Starting MCP HTTP Server on {settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
    logger.info("Available tools: transcribe_audio, transcribe_batch, get_server_status, list_supported_formats")
    
    # Run the MCP server
    mcp.run()

if __name__ == "__main__":
    main()
