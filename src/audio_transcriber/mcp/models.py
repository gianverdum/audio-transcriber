"""
Pydantic models for MCP Server audio transcription
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field, validator
from datetime import datetime


class TranscribeAudioInput(BaseModel):
    """Input schema for audio transcription via MCP"""
    
    audio_url: HttpUrl = Field(
        description="URL of the audio file to transcribe"
    )
    language: Optional[str] = Field(
        default=None,
        description="Audio language in ISO-639-1 format (e.g., 'pt', 'en', 'es')"
    )
    max_file_size_mb: Optional[int] = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum file size in MB"
    )
    timeout_seconds: Optional[int] = Field(
        default=300,
        ge=30,
        le=900,
        description="Timeout for transcription in seconds"
    )
    
    @validator('language')
    def validate_language(cls, v):
        """Validate language code format"""
        if v is not None and (len(v) != 2 or not v.isalpha() or not v.islower()):
            raise ValueError('Language must be a 2-letter ISO-639-1 code (e.g., "pt", "en")')
        return v


class TranscribeAudioOutput(BaseModel):
    """Output schema for audio transcription via MCP"""
    
    success: bool = Field(description="Whether transcription was successful")
    transcription: str = Field(description="Transcribed text (empty if failed)")
    filename: str = Field(description="Original filename from URL")
    file_size_mb: float = Field(description="File size in MB")
    language_detected: Optional[str] = Field(description="Language detected by Whisper")
    language_specified: Optional[str] = Field(description="Language specified in request")
    processing_time_seconds: float = Field(description="Time taken for transcription")
    timestamp: datetime = Field(description="When transcription was completed")
    model_used: str = Field(description="AI model used (e.g., whisper-1)")
    error: Optional[str] = Field(description="Error message if transcription failed")
    
    # Additional metadata for WhatsApp/messaging integration
    audio_url: str = Field(description="Original audio URL")
    audio_format: Optional[str] = Field(description="Detected audio format")
    download_time_seconds: Optional[float] = Field(description="Time taken to download file")


class BatchTranscribeInput(BaseModel):
    """Input schema for batch audio transcription via MCP"""
    
    audio_urls: List[HttpUrl] = Field(
        min_items=1,
        max_items=10,
        description="List of audio URLs to transcribe (max 10)"
    )
    language: Optional[str] = Field(
        default=None,
        description="Audio language in ISO-639-1 format (applies to all files)"
    )
    max_file_size_mb: Optional[int] = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum file size in MB per file"
    )
    timeout_seconds: Optional[int] = Field(
        default=300,
        ge=30,
        le=900,
        description="Timeout per file in seconds"
    )
    
    @validator('language')
    def validate_language(cls, v):
        """Validate language code format"""
        if v is not None and (len(v) != 2 or not v.isalpha() or not v.islower()):
            raise ValueError('Language must be a 2-letter ISO-639-1 code (e.g., "pt", "en")')
        return v


class BatchTranscribeOutput(BaseModel):
    """Output schema for batch audio transcription via MCP"""
    
    success: bool = Field(description="Whether batch processing completed")
    total_files: int = Field(description="Total number of files processed")
    successful_transcriptions: int = Field(description="Number of successful transcriptions")
    failed_transcriptions: int = Field(description="Number of failed transcriptions")
    results: List[TranscribeAudioOutput] = Field(description="Individual transcription results")
    total_processing_time_seconds: float = Field(description="Total time for batch processing")
    timestamp: datetime = Field(description="When batch processing was completed")


class ServerStatusOutput(BaseModel):
    """Output schema for server status check"""
    
    status: str = Field(description="Server status (healthy/unhealthy)")
    version: str = Field(description="Audio Transcriber version")
    mcp_version: str = Field(description="MCP protocol version")
    openai_api_available: bool = Field(description="Whether OpenAI API is accessible")
    supported_formats: List[str] = Field(description="Supported audio formats")
    max_file_size_mb: int = Field(description="Maximum file size allowed")
    timestamp: datetime = Field(description="Status check timestamp")
    uptime_seconds: Optional[float] = Field(description="Server uptime in seconds")


class MCPError(BaseModel):
    """Error response schema for MCP Server"""
    
    error_type: str = Field(description="Type of error")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(description="Additional error details")
    timestamp: datetime = Field(description="When error occurred")
    request_id: Optional[str] = Field(description="Request ID for tracking")
