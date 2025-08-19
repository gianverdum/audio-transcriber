"""
Modelos Pydantic para API do Audio Transcriber
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict  # type: ignore[import]
from datetime import datetime


class TranscriptionRequest(BaseModel):
    """Modelo para requisição de transcrição"""
    
    # Arquivo será enviado via multipart/form-data
    output_format: Literal["json", "txt", "xlsx", "csv"] = Field(
        default="json",
        description="Formato de saída desejado"
    )
    
    # Configurações opcionais
    max_file_size_mb: Optional[int] = Field(
        default=25,
        description="Tamanho máximo do arquivo em MB",
        ge=1,
        le=100
    )
    
    language: Optional[str] = Field(
        default=None,
        description="Idioma do áudio (auto-detectado se não especificado)"
    )
    
    response_format: Literal["text", "json", "verbose_json"] = Field(
        default="text",
        description="Formato de resposta da OpenAI"
    )


class TranscriptionResponse(BaseModel):
    """Modelo para resposta de transcrição"""
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "success": True,
                "transcription": "Olá, este é um exemplo de transcrição de áudio.",
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
    
    success: bool = Field(description="Se a transcrição foi bem-sucedida")
    transcription: str = Field(description="Texto transcrito")
    
    # Metadados
    filename: str = Field(description="Nome do arquivo original")
    file_size_mb: float = Field(description="Tamanho do arquivo em MB")
    processing_time_seconds: float = Field(description="Tempo de processamento")
    timestamp: datetime = Field(description="Data/hora do processamento")
    
    # Informações técnicas
    model_used: str = Field(default="whisper-1", description="Modelo usado")
    output_format: str = Field(description="Formato de saída")
    
    # Erro (se houver)
    error: Optional[str] = Field(default=None, description="Mensagem de erro")


class BatchTranscriptionRequest(BaseModel):
    """Modelo para transcrição em lote"""
    
    output_format: Literal["json", "txt", "xlsx", "csv"] = Field(
        default="xlsx",
        description="Formato de saída desejado"
    )
    
    max_file_size_mb: Optional[int] = Field(
        default=25,
        description="Tamanho máximo por arquivo em MB"
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Incluir metadados na resposta"
    )


class BatchTranscriptionResponse(BaseModel):
    """Modelo para resposta de transcrição em lote"""
    
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    success: bool = Field(description="Se o processamento foi bem-sucedido")
    total_files: int = Field(description="Total de arquivos processados")
    successful_transcriptions: int = Field(description="Transcrições bem-sucedidas")
    failed_transcriptions: int = Field(description="Transcrições falhadas")
    
    # Resultados individuais
    results: List[TranscriptionResponse] = Field(description="Resultados individuais")
    
    # Metadados do lote
    processing_time_seconds: float = Field(description="Tempo total de processamento")
    timestamp: datetime = Field(description="Data/hora do processamento")
    output_format: str = Field(description="Formato de saída")
    
    # URL de download (para formatos de arquivo)
    download_url: Optional[str] = Field(
        default=None,
        description="URL para download do arquivo gerado"
    )


class HealthResponse(BaseModel):
    """Modelo para resposta de health check"""
    
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
    
    status: Literal["healthy", "unhealthy"] = Field(description="Status da API")
    version: str = Field(description="Versão da aplicação")
    timestamp: datetime = Field(description="Data/hora da verificação")
    
    # Verificações de dependências
    openai_api_available: bool = Field(description="Se a API da OpenAI está disponível")
    
    # Informações do sistema
    supported_formats: List[str] = Field(description="Formatos de áudio suportados")
    max_file_size_mb: int = Field(description="Tamanho máximo de arquivo")


class ErrorResponse(BaseModel):
    """Modelo para respostas de erro"""
    
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    error: str = Field(description="Tipo do erro")
    message: str = Field(description="Mensagem de erro")
    details: Optional[str] = Field(default=None, description="Detalhes adicionais")
    timestamp: datetime = Field(description="Data/hora do erro")
    request_id: Optional[str] = Field(default=None, description="ID da requisição")
