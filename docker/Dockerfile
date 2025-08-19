# Dockerfile para Audio Transcriber API
FROM python:3.11-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de configuração
COPY pyproject.toml uv.lock* ./

# Instala uv
RUN pip install uv

# Copia código fonte
COPY src/ ./src/
COPY .env.example .env

# Instala dependências
RUN uv sync --frozen

# Muda para usuário não-root
RUN chown -R appuser:appuser /app
USER appuser

# Expõe porta
EXPOSE 8000

# Comando padrão
CMD ["uv", "run", "uvicorn", "audio_transcriber.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
