"""
Pydantic Models for Audio Transcriber API
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict  # type: ignore[import]
from datetime import datetime


class TranscriptionRequest(BaseModel):
    """Model for transcription request"""

    # File will be sent via multipart/form-data
    output_format: Literal["json", "txt", "xlsx", "csv"] = Field(
        default="json",
        description="Desired output format"
    )

    # Optional configurations
    max_file_size_mb: Optional[int] = Field(
        default=25,
        description="Maximum file size in MB",
        ge=1,
        le=100
    )
    
    language: Optional[str] = Field(
        default=None,
        description="Language of the audio (auto-detected if not specified)"
    )
    
    response_format: Literal["text", "json", "verbose_json"] = Field(
        default="text",
        description="Response format from OpenAI"
    )


class TranscriptionResponse(BaseModel):
    """Model for transcription response"""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "success": True,
                "transcription": "Hello, this is an example of audio transcription.",
                "filename": "audio.mp3",
                "file_size_mb": 2.5,
                "processing_time_seconds": 1.8,
                "timestamp": "2025-08-19T15:30:00.123456",
                "model_used": "whisper-1",
                "output_format": "json",
                "error": None
            }
        }
    )

    success: bool = Field(description="If the transcription was successful")
    transcription: str = Field(description="Transcribed text")

    # Metadata
    filename: str = Field(description="Original file name")
    file_size_mb: float = Field(description="File size in MB")
    processing_time_seconds: float = Field(description="Processing time in seconds")
    timestamp: datetime = Field(description="Processing date/time")

    # Technical information
    model_used: str = Field(default="whisper-1", description="Model used")
    output_format: str = Field(description="Formato de saída")

    # Error (if any)
    error: Optional[str] = Field(default=None, description="Error message")


class BatchTranscriptionRequest(BaseModel):
    """Model for batch transcription"""

    output_format: Literal["json", "txt", "xlsx", "csv"] = Field(
        default="xlsx",
        description="Desired output format"
    )
    
    max_file_size_mb: Optional[int] = Field(
        default=25,
        description="Maximum file size per file in MB"
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Include metadata in the response"
    )


class BatchTranscriptionResponse(BaseModel):
    """Model for batch transcription response"""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    success: bool = Field(description="If the processing was successful")
    total_files: int = Field(description="Total number of files processed")
    successful_transcriptions: int = Field(description="Successful transcriptions")
    failed_transcriptions: int = Field(description="Failed transcriptions")

    # Individual results
    results: List[TranscriptionResponse] = Field(description="Individual results")

    # Batch metadata
    processing_time_seconds: float = Field(description="Total processing time")
    timestamp: datetime = Field(description="Processing date/time")
    output_format: str = Field(description="Output format")

    # Download URL (for file formats)
    download_url: Optional[str] = Field(
        default=None,
        description="URL for downloading the generated file"
    )


class HealthResponse(BaseModel):
    """Model for health check response"""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-08-19T15:30:00.123456",
                "openai_api_available": True,
                "supported_formats": [".mp3", ".wav", ".ogg", ".m4a", ".flac"],
                "max_file_size_mb": 25
            }
        }
    )

    status: Literal["healthy", "unhealthy"] = Field(description="API status")
    version: str = Field(description="Application version")
    timestamp: datetime = Field(description="Check date/time")

    # Dependency checks
    openai_api_available: bool = Field(description="If the OpenAI API is available")

    # System information
    supported_formats: List[str] = Field(description="Supported audio formats")
    max_file_size_mb: int = Field(description="Maximum file size")


class ErrorResponse(BaseModel):
    """Model for error responses"""
    
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[str] = Field(default=None, description="Additional details")
    timestamp: datetime = Field(description="Error date/time")
    request_id: Optional[str] = Field(default=None, description="Request ID")
