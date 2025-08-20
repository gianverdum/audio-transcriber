---
applyTo: '**'
---

# English-Only Codebase Guidelines

## Language Standards

**All code elements MUST be written in English**, including but not limited to:

- **Variable names**: `user_name`, `audio_file_path`, `transcription_result`
- **Function names**: `transcribe_audio()`, `validate_input()`, `process_batch()`
- **Class names**: `AudioTranscriber`, `MCPTranscriptionService`, `ConfigurationManager`
- **Method names**: `get_server_status()`, `download_audio_file()`, `create_excel_report()`
- **Constants**: `MAX_FILE_SIZE_MB`, `SUPPORTED_FORMATS`, `DEFAULT_TIMEOUT`
- **Comments**: All inline and block comments
- **Docstrings**: Function, class, and module documentation
- **Error messages**: Exception messages and error descriptions
- **Log messages**: All logging output
- **Configuration keys**: Environment variables and settings
- **API endpoints**: Route names and descriptions
- **Database fields**: Column names and table names (if applicable)
- **Test names**: Test function and class names
- **File and directory names**: Module names, package names

## Code Examples

### ✅ Correct (English)
```python
def transcribe_audio_from_url(audio_url: str, language: Optional[str] = None) -> TranscriptionResult:
    """
    Transcribe audio file from URL using OpenAI Whisper.
    
    Args:
        audio_url: URL of the audio file to transcribe
        language: Optional language code (ISO-639-1 format)
        
    Returns:
        Transcription result with text and metadata
        
    Raises:
        ValueError: If URL is invalid or file is too large
    """
    try:
        # Download audio file from URL
        audio_content = download_file(audio_url)
        
        # Validate file size and format
        if not is_valid_audio_format(audio_content):
            raise ValueError("Unsupported audio format")
            
        # Process transcription
        transcription_text = openai_transcribe(audio_content, language)
        
        logger.info(f"Successfully transcribed audio from {audio_url}")
        return TranscriptionResult(text=transcription_text, success=True)
        
    except Exception as error:
        logger.error(f"Failed to transcribe audio: {error}")
        return TranscriptionResult(text="", success=False, error=str(error))
```

### ❌ Incorrect (Portuguese/Mixed Languages)
```python
def transcrever_audio_da_url(url_audio: str, idioma: Optional[str] = None) -> ResultadoTranscricao:
    """
    Transcreve arquivo de áudio da URL usando Whisper da OpenAI.
    """
    try:
        # Baixar arquivo de áudio da URL
        conteudo_audio = baixar_arquivo(url_audio)
        
        # Validar tamanho e formato
        if not eh_formato_valido(conteudo_audio):
            raise ValueError("Formato de áudio não suportado")
            
        logger.info(f"Áudio transcrito com sucesso de {url_audio}")
        
    except Exception as erro:
        logger.error(f"Falha ao transcrever áudio: {erro}")
```

## Exception: Explicit Language Requirements

The **ONLY** exception to this rule is when:

1. **User explicitly requests** content in another language in their prompt
2. **Documentation** intended for non-English speaking users (README translations, etc.)
3. **User-facing messages** that need localization
4. **Test data** that specifically tests non-English content

### Examples of Valid Non-English Usage

```python
# When user explicitly asks for Portuguese error messages
def get_error_message_pt(error_code: str) -> str:
    """Return error message in Portuguese as requested by user."""
    error_messages_pt = {
        "invalid_file": "Arquivo inválido",
        "file_too_large": "Arquivo muito grande"
    }
    return error_messages_pt.get(error_code, "Erro desconhecido")

# Test data for non-English content
def test_transcription_portuguese():
    """Test transcription with Portuguese audio content."""
    test_cases = [
        "Olá, como você está?",  # Portuguese test phrase
        "Bom dia, tudo bem?"     # Portuguese test phrase
    ]
```

## Implementation Guidelines

### Variable Naming Conventions
- Use **descriptive English names**: `transcription_service` not `ts` or `servico_transcricao`
- Use **snake_case** for variables and functions: `audio_file_path`, `process_batch_request`
- Use **PascalCase** for classes: `AudioTranscriber`, `MCPServer`, `TranscriptionResult`
- Use **UPPER_SNAKE_CASE** for constants: `MAX_FILE_SIZE_MB`, `DEFAULT_LANGUAGE`

### Comment Standards
```python
# ✅ Good: Clear English comments
def calculate_processing_time(start_time: float) -> float:
    """Calculate the total processing time in seconds."""
    return time.time() - start_time

# ❌ Bad: Portuguese comments
def calcular_tempo_processamento(tempo_inicio: float) -> float:
    """Calcula o tempo total de processamento em segundos."""
    return time.time() - tempo_inicio
```

### Documentation Standards
- **API documentation**: All OpenAPI/Swagger descriptions in English
- **README files**: Primary documentation in English (translations as separate files)
- **Code comments**: Explain complex logic in clear English
- **Error messages**: User-facing errors can be localized, but internal errors in English

### Configuration and Environment Variables
```bash
# ✅ Correct
OPENAI_API_KEY=sk-proj-...
MAX_FILE_SIZE_MB=25
SERVER_HOST=127.0.0.1
LOG_LEVEL=INFO

# ❌ Incorrect
CHAVE_OPENAI=sk-proj-...
TAMANHO_MAX_ARQUIVO_MB=25
SERVIDOR_HOST=127.0.0.1
NIVEL_LOG=INFO
```

## Quality Assurance

### Code Review Checklist
- [ ] All variable names are in English
- [ ] All function/method names are in English
- [ ] All comments and docstrings are in English
- [ ] All error messages are in English (unless explicitly localized)
- [ ] All log messages are in English
- [ ] Configuration keys follow English naming

### Automated Checks
Consider implementing linting rules to enforce English-only naming:
- Variable name patterns
- Function name patterns  
- Comment language detection
- Docstring language validation

## Rationale

### Why English-Only?

1. **International Collaboration**: English is the de facto standard for software development
2. **Code Maintainability**: Consistent language reduces cognitive load
3. **Open Source Friendliness**: Enables global contributors to understand and contribute
4. **Professional Standards**: Aligns with industry best practices
5. **Tool Compatibility**: Most development tools and IDEs expect English
6. **Documentation Integration**: Seamless integration with English documentation
7. **Error Debugging**: Easier to search for solutions online
8. **Team Scalability**: New team members can understand code regardless of native language

### Benefits

- **Reduced Context Switching**: Developers don't need to mentally translate between languages
- **Better Tooling Support**: IDE autocomplete, static analysis tools work better with English
- **Easier Code Reviews**: Reviewers can focus on logic rather than language barriers
- **Improved Collaboration**: Global team members can contribute effectively
- **Standard Compliance**: Follows established software engineering practices

## Migration Strategy

For existing non-English code:
1. **Gradual Refactoring**: Update variable/function names during regular maintenance
2. **Priority-Based**: Focus on public APIs and frequently modified code first  
3. **Documentation First**: Ensure all new documentation is in English
4. **Team Training**: Ensure all team members understand the English-only policy

Remember: **Code is written once but read many times**. Investing in clear, English naming and documentation pays dividends in long-term maintainability and team productivity.
