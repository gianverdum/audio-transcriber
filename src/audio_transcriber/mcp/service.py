"""
MCP Service for Audio Transcription
Handles audio download and transcription logic for MCP protocol
"""

import asyncio
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import httpx
from urllib.parse import urlparse

from ..core.transcriber import AudioTranscriber
from ..core.config import settings
from .models import (
    TranscribeAudioInput,
    TranscribeAudioOutput,
    BatchTranscribeInput,
    BatchTranscribeOutput,
    ServerStatusOutput,
    MCPError
)

logger = logging.getLogger(__name__)


class MCPTranscriptionService:
    """Service for handling MCP audio transcription requests"""
    
    def __init__(self):
        """Initialize the MCP transcription service"""
        self.transcriber = AudioTranscriber()
        self.start_time = time.time()
        self.supported_formats = AudioTranscriber.SUPPORTED_FORMATS
        
    async def get_server_status(self) -> ServerStatusOutput:
        """Get server status and health information"""
        try:
            # Test OpenAI connectivity
            openai_available = True
            try:
                # Quick test to see if we can create a client
                test_client = self.transcriber.client
                openai_available = test_client is not None
            except Exception:
                openai_available = False
            
            uptime = time.time() - self.start_time
            
            return ServerStatusOutput(
                status="healthy" if openai_available else "degraded",
                version="1.0.0",
                mcp_version="1.13.0",
                openai_api_available=openai_available,
                supported_formats=list(self.supported_formats),
                max_file_size_mb=settings.MAX_FILE_SIZE_MB,
                timestamp=datetime.now(),
                uptime_seconds=uptime
            )
            
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return ServerStatusOutput(
                status="unhealthy",
                version="1.0.0",
                mcp_version="1.13.0",
                openai_api_available=False,
                supported_formats=list(self.supported_formats),
                max_file_size_mb=settings.MAX_FILE_SIZE_MB,
                timestamp=datetime.now(),
                uptime_seconds=time.time() - self.start_time
            )
    
    async def download_audio_file(
        self, 
        url: str, 
        max_size_mb: int = 25,
        timeout_seconds: int = 300
    ) -> Tuple[bytes, str, float]:
        """
        Download audio file from URL
        
        Args:
            url: Audio file URL
            max_size_mb: Maximum file size in MB
            timeout_seconds: Download timeout
            
        Returns:
            Tuple of (file_content, filename, download_time)
            
        Raises:
            Exception: If download fails or file is too large
        """
        start_time = time.time()
        
        try:
            # Parse URL to get filename
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename:
                filename = "audio_file"
            
            # Ensure filename has an extension
            if not Path(filename).suffix:
                filename += ".mp3"  # Default extension
            
            # Download file with httpx
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                logger.info(f"Downloading audio from: {url}")
                
                # Stream download to check size
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    
                    # Check content length if available
                    content_length = response.headers.get('content-length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > max_size_mb:
                            raise Exception(f"File too large: {size_mb:.2f}MB (max: {max_size_mb}MB)")
                    
                    # Download content
                    content = b""
                    async for chunk in response.aiter_bytes():
                        content += chunk
                        
                        # Check size during download
                        current_size_mb = len(content) / (1024 * 1024)
                        if current_size_mb > max_size_mb:
                            raise Exception(f"File too large: {current_size_mb:.2f}MB (max: {max_size_mb}MB)")
            
            download_time = time.time() - start_time
            logger.info(f"Downloaded {len(content)} bytes in {download_time:.2f}s")
            
            return content, filename, download_time
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error downloading file: {e.response.status_code}")
        except httpx.TimeoutException:
            raise Exception(f"Download timeout after {timeout_seconds}s")
        except Exception as e:
            raise Exception(f"Download error: {str(e)}")
    
    def validate_audio_format(self, filename: str) -> str:
        """
        Validate audio file format
        
        Args:
            filename: Audio filename
            
        Returns:
            File extension
            
        Raises:
            Exception: If format is not supported
        """
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise Exception(
                f"Unsupported audio format: {extension}. "
                f"Supported formats: {', '.join(sorted(self.supported_formats))}"
            )
        
        return extension
    
    async def transcribe_audio_from_url(self, input_data: TranscribeAudioInput) -> TranscribeAudioOutput:
        """
        Transcribe audio from URL
        
        Args:
            input_data: Transcription input parameters
            
        Returns:
            Transcription result
        """
        start_time = time.time()
        download_time = 0.0
        
        try:
            # Download audio file
            audio_content, filename, download_time = await self.download_audio_file(
                str(input_data.audio_url),
                input_data.max_file_size_mb,
                input_data.timeout_seconds
            )
            
            # Validate format
            audio_format = self.validate_audio_format(filename)
            
            # Calculate file size
            file_size_mb = len(audio_content) / (1024 * 1024)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=audio_format, delete=False) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = Path(temp_file.name)
            
            try:
                # Transcribe audio
                transcription, success, error = self.transcriber.transcribe_audio(
                    temp_file_path,
                    language=input_data.language
                )
                
                processing_time = time.time() - start_time
                
                if success:
                    return TranscribeAudioOutput(
                        success=True,
                        transcription=transcription,
                        filename=filename,
                        file_size_mb=file_size_mb,
                        language_detected=None,  # Whisper doesn't return detected language
                        language_specified=input_data.language,
                        processing_time_seconds=processing_time,
                        timestamp=datetime.now(),
                        model_used="whisper-1",
                        error=None,
                        audio_url=str(input_data.audio_url),
                        audio_format=audio_format,
                        download_time_seconds=download_time
                    )
                else:
                    return TranscribeAudioOutput(
                        success=False,
                        transcription="",
                        filename=filename,
                        file_size_mb=file_size_mb,
                        language_detected=None,
                        language_specified=input_data.language,
                        processing_time_seconds=processing_time,
                        timestamp=datetime.now(),
                        model_used="whisper-1",
                        error=error,
                        audio_url=str(input_data.audio_url),
                        audio_format=audio_format,
                        download_time_seconds=download_time
                    )
                    
            finally:
                # Clean up temporary file
                try:
                    temp_file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
                    
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Transcription error: {e}")
            
            return TranscribeAudioOutput(
                success=False,
                transcription="",
                filename=str(input_data.audio_url).split('/')[-1] or "unknown",
                file_size_mb=0.0,
                language_detected=None,
                language_specified=input_data.language,
                processing_time_seconds=processing_time,
                timestamp=datetime.now(),
                model_used="whisper-1",
                error=str(e),
                audio_url=str(input_data.audio_url),
                audio_format=None,
                download_time_seconds=download_time
            )
    
    async def transcribe_batch_from_urls(self, input_data: BatchTranscribeInput) -> BatchTranscribeOutput:
        """
        Transcribe multiple audio files from URLs in batch
        
        Args:
            input_data: Batch transcription input parameters
            
        Returns:
            Batch transcription results
        """
        start_time = time.time()
        results = []
        
        # Process each URL
        tasks = []
        for audio_url in input_data.audio_urls:
            single_input = TranscribeAudioInput(
                audio_url=audio_url,
                language=input_data.language,
                max_file_size_mb=input_data.max_file_size_mb,
                timeout_seconds=input_data.timeout_seconds
            )
            tasks.append(self.transcribe_audio_from_url(single_input))
        
        # Execute transcriptions concurrently (but with delay between OpenAI calls)
        for i, task in enumerate(tasks):
            if i > 0:
                # Add delay between requests to respect rate limits
                await asyncio.sleep(settings.API_DELAY)
            
            result = await task
            results.append(result)
        
        # Calculate summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_time = time.time() - start_time
        
        return BatchTranscribeOutput(
            success=True,
            total_files=len(results),
            successful_transcriptions=successful,
            failed_transcriptions=failed,
            results=results,
            total_processing_time_seconds=total_time,
            timestamp=datetime.now()
        )
