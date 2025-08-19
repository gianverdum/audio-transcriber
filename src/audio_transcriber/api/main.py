"""
API FastAPI para Audio Transcriber
Fornece endpoints REST para transcrição de áudios
"""

import tempfile
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status  # type: ignore[import]
from fastapi.responses import Response, JSONResponse  # type: ignore[import]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import]
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

# Cria instância da aplicação
app = FastAPI(
    title="Audio Transcriber API",
    description="""
    ## 🎵 API para Transcrição de Áudios usando OpenAI Whisper
    
    Esta API permite transcrever arquivos de áudio em texto usando o modelo Whisper da OpenAI.
    
    ### 📋 Formatos Suportados
    - **Áudio**: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, flac
    - **Saída**: json, txt, xlsx, csv
    
    ### 🌍 Idiomas Suportados (ISO-639-1)
    - `pt` - Português
    - `en` - Inglês
    - `es` - Espanhol
    - `fr` - Francês
    - `de` - Alemão
    - `it` - Italiano
    - `ja` - Japonês
    - `ko` - Coreano
    - `zh` - Chinês
    - `ru` - Russo
    - E muitos outros...
    
    ### 📏 Limites
    - **Tamanho máximo**: 25MB por arquivo
    - **Timeout**: 30 segundos por arquivo
    
    ### 🚀 Endpoints Disponíveis
    - `/transcribe` - Transcrição de arquivo único (resposta JSON)
    - `/transcribe/batch` - Transcrição de múltiplos arquivos
    - `/transcribe/download` - Transcrição com download direto do resultado
    - `/languages` - Lista de idiomas suportados
    - `/health` - Verificação de saúde da API
    
    ### ⚠️ Códigos de Erro Comuns
    - **400**: Arquivo inválido, formato não suportado, ou parâmetros incorretos
    - **413**: Arquivo muito grande (> 25MB)
    - **422**: Dados de entrada mal formatados
    - **503**: Serviço temporariamente indisponível
    - **500**: Erro interno do servidor
    
    ### 💡 Dicas de Uso
    1. **Idioma**: Use códigos ISO-639-1 de 2 letras (ex: 'pt', não 'pt-BR')
    2. **Qualidade**: Áudios com boa qualidade geram melhores transcrições
    3. **Formato**: MP3 e WAV são os formatos mais confiáveis
    4. **Timeout**: Arquivos grandes podem levar mais tempo para processar
    
    ### 📖 Documentação
    - Swagger UI (/docs) - Interface interativa
    - ReDoc (/redoc) - Documentação detalhada
    """,
    version="1.0.0",
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

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do serviço
transcription_service = None


@app.on_event("startup")
async def startup_event():
    """Inicializa serviços na startup"""
    global transcription_service
    try:
        transcription_service = TranscriptionService()
    except Exception as e:
        print(f"Erro ao inicializar serviço de transcrição: {e}")


@app.get("/", response_model=dict)
async def root():
    """Endpoint raiz"""
    return {
        "message": "Audio Transcriber API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", 
         response_model=HealthResponse,
         summary="Verificação de saúde da API",
         description="Verifica o status da API e suas dependências")
async def health_check():
    """
    ## Verificação de saúde da API
    
    Endpoint para monitoramento que verifica se a API está funcionando corretamente.
    
    ### Exemplo de resposta saudável:
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
    
    ### Status possíveis:
    - **healthy**: API funcionando normalmente
    - **unhealthy**: Problemas detectados (ex: API OpenAI indisponível)
    
    ### Códigos de resposta:
    - **200**: Verificação realizada (status pode ser healthy ou unhealthy)
    """
    try:
        # Testa se pode criar instância do transcriber
        test_transcriber = AudioTranscriber()
        openai_available = test_transcriber.client is not None
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now(),
            openai_api_available=openai_available,
            supported_formats=list(AudioTranscriber.SUPPORTED_FORMATS),
            max_file_size_mb=25
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            timestamp=datetime.now(),
            openai_api_available=False,
            supported_formats=list(AudioTranscriber.SUPPORTED_FORMATS),
            max_file_size_mb=25
        )


@app.get("/languages",
         summary="Listar idiomas suportados",
         description="Lista todos os códigos de idioma aceitos pela API")
async def get_supported_languages():
    """
    ## Lista de idiomas suportados
    
    Retorna todos os códigos de idioma ISO-639-1 aceitos pela API Whisper da OpenAI.
    
    ### Exemplo de resposta:
    ```json
    {
        "supported_languages": {
            "pt": "Português",
            "en": "English",
            "es": "Español"
        },
        "total_languages": 97,
        "note": "Use os códigos de 2 letras (ex: 'pt') no parâmetro language"
    }
    ```
    """
    # Lista de idiomas suportados pelo Whisper (principais)
    languages = {
        "pt": "Português",
        "en": "English", 
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
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
        "note": "Use os códigos de 2 letras (ex: 'pt') no parâmetro language",
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
          summary="Transcrever arquivo único",
          description="Transcreve um único arquivo de áudio e retorna o resultado em JSON")
async def transcribe_audio(
    file: UploadFile = File(description="Arquivo de áudio para transcrever"),
    output_format: str = Form(
        default="json", 
        description="Formato de saída: json, txt, xlsx, csv"
    ),
    max_file_size_mb: Optional[int] = Form(
        default=25, 
        description="Tamanho máximo do arquivo em MB (1-100)",
        ge=1, le=100
    ),
    language: Optional[str] = Form(
        default=None, 
        description="Idioma do áudio em formato ISO-639-1 (ex: 'pt', 'en', 'es')"
    ),
):
    """
    ## Transcreve um único arquivo de áudio
    
    Realiza a transcrição de um arquivo de áudio usando o modelo Whisper da OpenAI.
    
    ### Exemplo de uso com cURL:
    ```bash
    curl -X POST "http://localhost:8000/transcribe" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@audio.mp3" \
         -F "output_format=json" \
         -F "language=pt"
    ```
    
    ### Exemplo de resposta:
    ```json
    {
        "success": true,
        "transcription": "Olá, este é um exemplo de transcrição.",
        "filename": "audio.mp3",
        "file_size_mb": 2.5,
        "processing_time_seconds": 1.5,
        "timestamp": "2025-08-19T15:30:00",
        "model_used": "whisper-1",
        "output_format": "json",
        "error": null
    }
    ```
    
    ### Códigos de resposta:
    - **200**: Transcrição realizada com sucesso
    - **400**: Arquivo inválido ou parâmetros incorretos
    - **413**: Arquivo muito grande
    - **500**: Erro interno do servidor
    """
    if not transcription_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de transcrição não disponível"
        )
    
    # Validações
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do arquivo é obrigatório"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in AudioTranscriber.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado. Formatos aceitos: {', '.join(AudioTranscriber.SUPPORTED_FORMATS)}"
        )
    
    # Lê conteúdo do arquivo
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao ler arquivo: {str(e)}"
        )
    
    # Verifica tamanho
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Máximo: {max_file_size_mb}MB"
        )
    
    # Processa transcrição
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
            detail=f"Erro na transcrição: {str(e)}"
        )


@app.post("/transcribe/batch", 
          response_model=BatchTranscriptionResponse,
          summary="Transcrever múltiplos arquivos",
          description="Transcreve múltiplos arquivos de áudio em lote")
async def transcribe_batch(
    files: List[UploadFile] = File(description="Lista de arquivos de áudio para transcrever"),
    output_format: str = Form(
        default="xlsx", 
        description="Formato de saída: json, txt, xlsx, csv"
    ),
    max_file_size_mb: Optional[int] = Form(
        default=25, 
        description="Tamanho máximo por arquivo em MB (1-100)",
        ge=1, le=100
    ),
    language: Optional[str] = Form(
        default=None, 
        description="Idioma dos áudios em formato ISO-639-1 (ex: 'pt', 'en', 'es')"
    ),
):
    """
    ## Transcreve múltiplos arquivos de áudio em lote
    
    Processa vários arquivos de áudio simultaneamente e retorna os resultados consolidados.
    
    ### Exemplo de uso com cURL:
    ```bash
    curl -X POST "http://localhost:8000/transcribe/batch" \
         -H "Content-Type: multipart/form-data" \
         -F "files=@audio1.mp3" \
         -F "files=@audio2.wav" \
         -F "output_format=xlsx" \
         -F "language=pt"
    ```
    
    ### Exemplo de resposta:
    ```json
    {
        "success": true,
        "total_files": 2,
        "successful_transcriptions": 2,
        "failed_transcriptions": 0,
        "results": [
            {
                "success": true,
                "transcription": "Primeira transcrição...",
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
    
    ### Códigos de resposta:
    - **200**: Processamento concluído (pode haver falhas individuais)
    - **400**: Nenhum arquivo válido fornecido
    - **500**: Erro interno do servidor
    """
    if not transcription_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de transcrição não disponível"
        )
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pelo menos um arquivo é obrigatório"
        )
    
    # Valida e processa arquivos
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
            detail="Nenhum arquivo válido para processar"
        )
    
    # Processa lote
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
            detail=f"Erro no processamento em lote: {str(e)}"
        )


@app.post("/transcribe/download",
          summary="Transcrever e baixar resultado",
          description="Transcreve arquivos e retorna o resultado para download direto")
async def transcribe_and_download(
    files: List[UploadFile] = File(description="Arquivo(s) de áudio para transcrever"),
    output_format: str = Form(
        default="xlsx",
        description="Formato do arquivo de saída: json, txt, xlsx, csv"
    ),
    max_file_size_mb: Optional[int] = Form(
        default=25,
        description="Tamanho máximo por arquivo em MB (1-100)",
        ge=1, le=100
    ),
    language: Optional[str] = Form(
        default=None,
        description="Idioma dos áudios em formato ISO-639-1 (ex: 'pt', 'en', 'es')"
    ),
):
    """
    ## Transcreve arquivos e retorna resultado para download
    
    Processa um ou múltiplos arquivos de áudio e retorna o resultado formatado para download direto.
    
    ### Exemplo de uso com cURL:
    ```bash
    # Para arquivo único com saída Excel
    curl -X POST "http://localhost:8000/transcribe/download" \
         -H "Content-Type: multipart/form-data" \
         -F "files=@audio.mp3" \
         -F "output_format=xlsx" \
         -F "language=pt" \
         --output transcricao.xlsx
    
    # Para múltiplos arquivos com saída CSV
    curl -X POST "http://localhost:8000/transcribe/download" \
         -H "Content-Type: multipart/form-data" \
         -F "files=@audio1.mp3" \
         -F "files=@audio2.wav" \
         -F "output_format=csv" \
         -F "language=pt" \
         --output transcricoes.csv
    ```
    
    ### Formatos de resposta:
    - **xlsx**: Planilha Excel com dados estruturados
    - **csv**: Arquivo CSV com dados tabulares
    - **txt**: Arquivo de texto com transcrições
    - **json**: Resposta JSON estruturada
    
    ### Headers de resposta:
    - `Content-Type`: Tipo MIME apropriado ao formato
    - `Content-Disposition`: Nome do arquivo para download
    
    ### Códigos de resposta:
    - **200**: Download pronto com dados da transcrição
    - **400**: Arquivo inválido ou parâmetros incorretos
    - **413**: Arquivo muito grande
    - **500**: Erro interno do servidor
    """
    if not transcription_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de transcrição não disponível"
        )
    
    # Se apenas um arquivo, trata como single
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
        # Múltiplos arquivos
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
    
    # Formata saída
    try:
        formatted_output = transcription_service.format_output(result, output_format)
        
        if output_format == "json":
            return JSONResponse(content=formatted_output)
        
        elif output_format == "txt":
            return Response(
                content=formatted_output,
                media_type="text/plain",
                headers={"Content-Disposition": "attachment; filename=transcricao.txt"}
            )
        
        elif output_format in ["xlsx", "csv"]:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if output_format == "xlsx" else "text/csv"
            filename = f"transcricao.{output_format}"
            
            return Response(
                content=formatted_output,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao formatar saída: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções"""
    error_response = ErrorResponse(
        error="InternalServerError",
        message="Erro interno do servidor",
        details=str(exc),
        timestamp=datetime.now(),
        request_id=str(uuid.uuid4())
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json')
    )


# Função para executar localmente
def run_local(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Executa a API localmente"""
    uvicorn.run(
        "audio_transcriber.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_local()
