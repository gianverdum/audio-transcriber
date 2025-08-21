"""
FastAPI API for Audio Transcriber
Provides REST endpoints for audio transcription
"""

import tempfile
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path


from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status, Depends, Header  # type: ignore[import]
from fastapi.responses import Response, JSONResponse  # type: ignore[import]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import]
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # type: ignore[import]
import uvicorn  # type: ignore[import]

from .models import (
    TranscriptionRequest,
    TranscriptionResponse,
    BatchTranscriptionRequest,
    BatchTranscriptionResponse,
    HealthResponse,
    ErrorResponse
)
from .service import TranscriptionService
from ..core import AudioTranscriber

from ..core.config import settings

# Logger for warnings and info
import logging
logger = logging.getLogger(__name__)

# Create application instance using centralized configurations
app = FastAPI(
    title=settings.API_TITLE,
    description=f"""
    ## 🎵 {settings.API_TITLE}
    
    {settings.API_DESCRIPTION}
    
    ### 📋 Supported Formats
    - **Audio**: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, flac
    - **Output**: json, txt, xlsx, csv
    
    ### 🌍 Supported Languages (ISO-639-1)
    - `pt` - Portuguese
    - `en` - English
    - `es` - Spanish
    - `fr` - French
    - `de` - German
    - `it` - Italian
    - `ja` - Japanese
    - `ko` - Korean
    - `zh` - Chinese
    - `ru` - Russian
    - And many others...
    
    ### 📏 Limits
    - **Maximum size**: 25MB per file
    - **Timeout**: 30 seconds per file
    
    ### 🚀 Available Endpoints
    - `/transcribe` - Single file transcription (JSON response)
    - `/transcribe/batch` - Multiple files transcription
    - `/transcribe/download` - Transcription with direct result download
    - `/languages` - List of supported languages
    - `/health` - API health check
    
    ### ⚠️ Common Error Codes
    - **400**: Invalid file, unsupported format, or incorrect parameters
    - **413**: File too large (> 25MB)
    - **422**: Malformed input data
    - **503**: Service temporarily unavailable
    - **500**: Internal server error
    
    ### 💡 Usage Tips
    1. **Language**: Use 2-letter ISO-639-1 codes (e.g., 'pt', not 'pt-BR')
    2. **Quality**: Good quality audio generates better transcriptions
    3. **Format**: MP3 and WAV are the most reliable formats
    4. **Timeout**: Large files may take longer to process
    
    ### 📖 Documentation
    - Swagger UI (/docs) - Interactive interface
    - ReDoc (/redoc) - Detailed documentation
    """,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Audio Transcriber API",
        "url": "http://localhost:8000/health",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
transcription_service = None

# Security setup
security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token if AUTH_TOKEN is set"""
    if not settings.AUTH_TOKEN:
        # No auth required if AUTH_TOKEN is not set
        return True
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if credentials.credentials != settings.AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global transcription_service
    try:
        transcription_service = TranscriptionService()
    except Exception as e:
        print(f"Error initializing transcription service: {e}")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "title": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
        "languages_url": "/languages",
        "status_url": "/status",
        "auth_required": bool(settings.AUTH_TOKEN)
    }


@app.get("/status", 
         response_model=dict,
         summary="API status with authentication",
         description="Protected endpoint that shows API status (requires auth if AUTH_TOKEN is set)")
async def get_status(authorized: bool = Depends(verify_token)):
    """
    ## API Status (Protected)
    
    Protected endpoint that shows detailed API status and configuration.
    Requires Bearer token authentication if AUTH_TOKEN environment variable is set.
    
    ### Usage with authentication:
    ```bash
    curl -H "Authorization: Bearer your_token_here" http://localhost:8000/status
    ```
    
    ### Example response:
    ```json
    {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": "2025-08-20T17:30:00.123456",
        "auth_enabled": true,
        "openai_configured": true,
        "server_config": {
            "host": "0.0.0.0",
            "port": 8000,
            "max_file_size_mb": 25
        }
    }
    ```
    """
    try:
        # Test OpenAI connection
        test_transcriber = AudioTranscriber()
        openai_configured = test_transcriber.client is not None
        
        return {
            "status": "operational",
            "version": settings.API_VERSION,
            "timestamp": datetime.now(),
            "auth_enabled": bool(settings.AUTH_TOKEN),
            "openai_configured": openai_configured,
            "server_config": {
                "host": settings.SERVER_HOST,
                "port": settings.SERVER_PORT,
                "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
                "api_timeout": settings.API_TIMEOUT,
                "log_level": settings.LOG_LEVEL
            },
            "supported_formats": list(AudioTranscriber.SUPPORTED_FORMATS),
            "endpoints": {
                "health": "/health",
                "transcribe": "/transcribe",
                "batch": "/transcribe/batch",
                "download": "/transcribe/download",
                "languages": "/languages",
                "docs": "/docs"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "version": settings.API_VERSION,
            "timestamp": datetime.now(),
            "auth_enabled": bool(settings.AUTH_TOKEN),
            "openai_configured": False,
            "error": str(e)
        }


@app.get("/health", 
         response_model=HealthResponse,
         summary="API health check",
         description="Checks API status and its dependencies")
async def health_check():
    """
    ## API Health Check
    
    Monitoring endpoint that checks if the API is working correctly.
    
    ### Example of healthy response:
    ```json
    {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-08-19T15:30:00.123456",
        "openai_api_available": true,
        "supported_formats": [".mp3", ".wav", ".ogg", ".m4a", ".flac"],
        "max_file_size_mb": 25
    }
    ```
    
    ### Possible statuses:
    - **healthy**: API working normally
    - **unhealthy**: Problems detected (e.g., OpenAI API unavailable)
    
    ### Response codes:
    - **200**: Check performed (status can be healthy or unhealthy)
    """
    try:
        # Test if transcriber instance can be created
        test_transcriber = AudioTranscriber()
        openai_available = test_transcriber.client is not None
        
        return HealthResponse(
            status="healthy",
            version=settings.API_VERSION,
            timestamp=datetime.now(),
            openai_api_available=openai_available,
            supported_formats=list(AudioTranscriber.SUPPORTED_FORMATS),
            max_file_size_mb=settings.MAX_FILE_SIZE_MB
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version=settings.API_VERSION,
            timestamp=datetime.now(),
            openai_api_available=False,
            supported_formats=list(AudioTranscriber.SUPPORTED_FORMATS),
            max_file_size_mb=settings.MAX_FILE_SIZE_MB
        )


@app.get("/languages",
         summary="List supported languages",
         description="Lists all language codes accepted by the API")
async def get_supported_languages():
    """
    ## List of supported languages
    
    Returns all ISO-639-1 language codes accepted by OpenAI's Whisper API.
    
    ### Example response:
    ```json
    {
        "supported_languages": {
            "pt": "Portuguese",
            "en": "English",
            "es": "Spanish"
        },
        "total_languages": 97,
        "note": "Use 2-letter codes (e.g., 'pt') in the language parameter"
    }
    ```
    """
    # List of languages supported by Whisper (main ones)
    languages = {
        "pt": "Portuguese",
        "en": "English", 
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "ja": "日本語",
        "ko": "한국어",
        "zh": "中文",
        "ru": "Русский",
        "ar": "العربية",
        "hi": "हिन्दी",
        "th": "ไทย",
        "vi": "Tiếng Việt",
        "nl": "Nederlands",
        "pl": "Polski",
        "tr": "Türkçe",
        "sv": "Svenska",
        "da": "Dansk",
        "no": "Norsk",
        "fi": "Suomi",
        "cs": "Čeština",
        "sk": "Slovenčina",
        "hu": "Magyar",
        "ro": "Română",
        "bg": "Български",
        "hr": "Hrvatski",
        "sl": "Slovenščina",
        "et": "Eesti",
        "lv": "Latviešu",
        "lt": "Lietuvių",
        "ca": "Català",
        "eu": "Euskera",
        "gl": "Galego",
        "is": "Íslenska",
        "mt": "Malti",
        "cy": "Cymraeg",
        "ga": "Gaeilge",
        "mk": "Македонски",
        "sq": "Shqip",
        "sr": "Српски",
        "bs": "Bosanski",
        "be": "Беларуская",
        "uk": "Українська",
        "el": "Ελληνικά",
        "he": "עברית",
        "fa": "فارسی",
        "ur": "اردو",
        "bn": "বাংলা",
        "ta": "தமிழ்",
        "te": "తెలుగు",
        "kn": "ಕನ್ನಡ",
        "ml": "മലയാളം",
        "gu": "ગુજરાતી",
        "mr": "मराठी",
        "ne": "नेपाली",
        "si": "සිංහල",
        "my": "မြန်မာ",
        "km": "ភាសាខ្មែរ",
        "lo": "ລາວ",
        "ka": "ქართული",
        "am": "አማርኛ",
        "az": "Azərbaycan",
        "kk": "Қазақ",
        "ky": "Кыргыз",
        "uz": "Oʻzbek",
        "tg": "Тоҷикӣ",
        "mn": "Монгол",
        "yo": "Yorùbá",
        "zu": "isiZulu",
        "af": "Afrikaans",
        "sw": "Kiswahili",
        "ha": "Hausa",
        "ig": "Igbo",
        "so": "Soomaali",
        "mg": "Malagasy",
        "eo": "Esperanto",
        "mi": "Te Reo Māori",
        "ms": "Bahasa Melayu",
        "id": "Bahasa Indonesia",
        "tl": "Filipino"
    }
    
    return {
        "supported_languages": languages,
        "total_languages": len(languages),
        "note": "Use 2-letter codes (e.g., 'pt') in the language parameter",
        "format": "ISO-639-1",
        "examples": {
            "portuguese": "pt",
            "english": "en", 
            "spanish": "es",
            "french": "fr",
            "german": "de"
        }
    }


@app.post("/transcribe", 
          response_model=TranscriptionResponse,
          summary="Transcribe single file",
          description="Transcribes a single audio file and returns the result in the specified format")
async def transcribe_audio(
    file: UploadFile = File(description="Audio file to transcribe"),
    output_format: str = Form(
        default="json", 
        description="Output format: json, txt, xlsx, csv"
    ),
    max_file_size_mb: Optional[int] = Form(
        default=25, 
        description="Maximum file size in MB (1-100)",
        ge=1, le=100
    ),
    language: Optional[str] = Form(
        default=None, 
        description="Audio language in ISO-639-1 format (e.g., 'pt', 'en', 'es')"
    ),
    authorized: bool = Depends(verify_token)
):
    """
    ## Transcribes a single audio file
    
    Performs audio transcription using OpenAI's Whisper model.
    
    ### Example usage with cURL:
    ```bash
    curl -X POST "http://localhost:8000/transcribe" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@audio.mp3" \
         -F "output_format=json" \
         -F "language=pt"
    ```
    
    ### Example response:
    ```json
    {
        "success": true,
        "transcription": "Hello, this is an example transcription.",
        "filename": "audio.mp3",
        "file_size_mb": 2.5,
        "processing_time_seconds": 1.5,
        "timestamp": "2025-08-19T15:30:00",
        "model_used": "whisper-1",
        "output_format": "json",
        "error": null
    }
    ```
    
    ### Response codes:
    - **200**: Transcription completed successfully
    - **400**: Invalid file or incorrect parameters
    - **413**: File too large
    - **500**: Internal server error
    """
    if not transcription_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription service not available"
        )
    
    # Validations
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in AudioTranscriber.SUPPORTED_FORMATS:
        logger.warning(f"File format {file_extension} not natively supported. Will attempt conversion in core logic.")
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Check size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum: {max_file_size_mb}MB"
        )
    
    # Process transcription
    try:
        result = await transcription_service.transcribe_single_file(
            file_content=file_content,
            filename=file.filename,
            output_format=output_format,
            language=language
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription error: {str(e)}"
        )


@app.post("/transcribe/batch", 
          response_model=BatchTranscriptionResponse,
          summary="Transcribe multiple files",
          description="Transcribes multiple audio files in batch")
async def transcribe_batch(
    files: List[UploadFile] = File(description="List of audio files to transcribe"),
    output_format: str = Form(
        default="xlsx", 
        description="Output format: json, txt, xlsx, csv"
    ),
    max_file_size_mb: Optional[int] = Form(
        default=25, 
        description="Maximum size per file in MB (1-100)",
        ge=1, le=100
    ),
    language: Optional[str] = Form(
        default=None, 
        description="Audio language in ISO-639-1 format (e.g., 'pt', 'en', 'es')"
    ),
):
    """
    ## Transcribes multiple audio files in batch
    
    Processes multiple audio files simultaneously and returns consolidated results.
    
    ### Example usage with cURL:
    ```bash
    curl -X POST "http://localhost:8000/transcribe/batch" \
         -H "Content-Type: multipart/form-data" \
         -F "files=@audio1.mp3" \
         -F "files=@audio2.wav" \
         -F "output_format=xlsx" \
         -F "language=pt"
    ```
    
    ### Example response:
    ```json
    {
        "success": true,
        "total_files": 2,
        "successful_transcriptions": 2,
        "failed_transcriptions": 0,
        "results": [
            {
                "success": true,
                "transcription": "First transcription...",
                "filename": "audio1.mp3",
                "file_size_mb": 1.2,
                "processing_time_seconds": 0.8,
                "timestamp": "2025-08-19T15:30:00",
                "model_used": "whisper-1",
                "output_format": "xlsx",
                "error": null
            }
        ],
        "processing_time_seconds": 2.1,
        "timestamp": "2025-08-19T15:30:00",
        "output_format": "xlsx"
    }
    ```
    
    ### Response codes:
    - **200**: Processing completed (may have individual failures)
    - **400**: No valid files provided
    - **500**: Internal server error
    """
    if not transcription_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription service not available"
        )
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required"
        )
    
    # Validate and process files
    file_data = []
    for file in files:
        if not file.filename:
            continue
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in AudioTranscriber.SUPPORTED_FORMATS:
            continue
        
        try:
            content = await file.read()
            file_size_mb = len(content) / (1024 * 1024)
            
            if file_size_mb <= max_file_size_mb:
                file_data.append((content, file.filename))
        except Exception:
            continue
    
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid files to process"
        )
    
    # Process batch
    try:
        result = await transcription_service.transcribe_batch(
            files=file_data,
            output_format=output_format,
            language=language
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing error: {str(e)}"
        )


@app.post("/transcribe/download",
          summary="Transcribe and download result",
          description="Transcribes files and returns the result for direct download")
async def transcribe_and_download(
    files: List[UploadFile] = File(description="Audio file(s) to transcribe"),
    output_format: str = Form(
        default="xlsx",
        description="Output file format: json, txt, xlsx, csv"
    ),
    max_file_size_mb: Optional[int] = Form(
        default=25,
        description="Maximum size per file in MB (1-100)",
        ge=1, le=100
    ),
    language: Optional[str] = Form(
        default=None,
        description="Audio language in ISO-639-1 format (e.g., 'pt', 'en', 'es')"
    ),
):
    """
    ## Transcribes files and returns result for download
    
    Processes one or multiple audio files and returns the formatted result for direct download.
    
    ### Example usage with cURL:
    ```bash
    # For single file with Excel output
    curl -X POST "http://localhost:8000/transcribe/download" \
         -H "Content-Type: multipart/form-data" \
         -F "files=@audio.mp3" \
         -F "output_format=xlsx" \
         -F "language=pt" \
         --output transcription.xlsx
    
    # For multiple files with CSV output
    curl -X POST "http://localhost:8000/transcribe/download" \
         -H "Content-Type: multipart/form-data" \
         -F "files=@audio1.mp3" \
         -F "files=@audio2.wav" \
         -F "output_format=csv" \
         -F "language=pt" \
         --output transcriptions.csv
    ```
    
    ### Response formats:
    - **xlsx**: Excel spreadsheet with structured data
    - **csv**: CSV file with tabular data
    - **txt**: Text file with transcriptions
    - **json**: Structured JSON response
    
    ### Response headers:
    - `Content-Type`: MIME type appropriate to the format
    - `Content-Disposition`: Filename for download
    
    ### Response codes:
    - **200**: Download ready with transcription data
    - **400**: Invalid file or incorrect parameters
    - **413**: File too large
    - **500**: Internal server error
    """
    if not transcription_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription service not available"
        )
    
    # If only one file, treat as single
    if len(files) == 1:
        file = files[0]
        file_content = await file.read()
        
        result = await transcription_service.transcribe_single_file(
            file_content=file_content,
            filename=file.filename,
            output_format=output_format,
            language=language
        )
    else:
        # Multiple files
        file_data = []
        for file in files:
            if file.filename:
                content = await file.read()
                file_data.append((content, file.filename))
        
        result = await transcription_service.transcribe_batch(
            files=file_data,
            output_format=output_format,
            language=language
        )
    
    # Format output
    try:
        formatted_output = transcription_service.format_output(result, output_format)
        
        if output_format == "json":
            return JSONResponse(content=formatted_output)
        
        elif output_format == "txt":
            return Response(
                content=formatted_output,
                media_type="text/plain",
                headers={"Content-Disposition": "attachment; filename=transcription.txt"}
            )
        
        elif output_format in ["xlsx", "csv"]:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if output_format == "xlsx" else "text/csv"
            filename = f"transcription.{output_format}"
            
            return Response(
                content=formatted_output,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output formatting error: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    error_response = ErrorResponse(
        error="InternalServerError",
        message="Internal server error",
        details=str(exc),
        timestamp=datetime.now(),
        request_id=str(uuid.uuid4())
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json')
    )


# Function to run locally
def run_local(
    host: Optional[str] = None, 
    port: Optional[int] = None, 
    reload: Optional[bool] = None,
    workers: Optional[int] = None
):
    """Runs the API locally using .env configurations as defaults"""
    
    # Use .env configurations as defaults
    final_host = host or settings.SERVER_HOST
    final_port = port or settings.SERVER_PORT
    final_reload = reload if reload is not None else settings.SERVER_RELOAD
    final_workers = workers or settings.SERVER_WORKERS
    
    # Print server information
    settings.print_server_info()
    
    uvicorn.run(
        "audio_transcriber.api.main:app",
        host=final_host,
        port=final_port,
        reload=final_reload,
        workers=final_workers if not final_reload else 1,  # Multiple workers only in production
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    run_local()
