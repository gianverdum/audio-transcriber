# 🎵 Audio Transcriber

Ferramenta completa para transcrição automática de arquivos de áudio usando a API da OpenAI, disponível como:

- **📱 CLI** - Interface de linha de comando
- **🌐 API REST** - Servidor web com FastAPI  
- **☁️ AWS Lambda** - Deploy serverless na nuvem
- **🐳 Docker** - Container para desenvolvimento e produção

## 📋 Características

- **Transcrição automática** usando o modelo Whisper da OpenAI
- **Múltiplos formatos de entrada**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, OGG, FLAC
- **Múltiplos formatos de saída**: JSON, TXT, Excel (XLSX), CSV
- **API REST completa** com documentação automática
- **Suporte a processamento em lote**
- **Deploy pronto para AWS Lambda**
- **Container Docker** para fácil deployment
- **Sistema de credenciais seguro** com arquivos .env
- **Tratamento de erros robusto** e logging detalhado

## 🚀 Instalação

### Opção 1: Usando UV (Recomendado)

```bash
# Clone o projeto
git clone <repository_url>
cd audio-transcriber

# Inicializa com uv
uv init .

# Adiciona dependências
uv add openai pandas openpyxl

# Instala dependências de desenvolvimento (opcional)
uv add --dev pytest pytest-cov black isort flake8 mypy
```

### Opção 2: Usando pip tradicional

```bash
# Clone o projeto
git clone <repository_url>
cd audio-transcriber

# Instala as dependências
pip install -e .

# Ou instala dependências diretamente
pip install openai pandas openpyxl
```

### Configuração da API OpenAI

O Audio Transcriber usa arquivo `.env` para gerenciar credenciais de forma segura.

**Passo 1: Criar arquivo de configuração**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Ou use o script utilitário
python scripts/setup_env.py
```

**Passo 2: Configurar sua chave da OpenAI**
1. Obtenha sua chave em: https://platform.openai.com/account/api-keys
2. Edite o arquivo `.env` e substitua `sua_chave_openai_aqui` pela sua chave real:
   ```bash
   OPENAI_API_KEY=sk-proj-sua_chave_real_aqui
   ```

**Alternativa: Variável de ambiente**
```bash
export OPENAI_API_KEY="sua_chave_openai_aqui"
```

> **⚠️ Importante:** Nunca commite o arquivo `.env` no git. Ele já está incluído no `.gitignore`.

## 📖 Como Usar

### 1️⃣ CLI (Linha de Comando)

```bash
# Transcrição local (modo tradicional)
audio-transcriber transcribe /caminho/para/pasta/audios
audio-transcriber transcribe /caminho/para/pasta/audios -o minhas_transcricoes.xlsx

# Servidor API local
audio-transcriber server
audio-transcriber server --host 0.0.0.0 --port 8000 --reload

# Compatibilidade: funciona sem subcomando
audio-transcriber /caminho/para/pasta/audios -o resultado.xlsx
```

### 2️⃣ API REST

```bash
# Inicia servidor
audio-transcriber server

# Ou diretamente
uv run uvicorn audio_transcriber.api.main:app --reload
```

**Endpoints disponíveis:**
- `GET /` - Informações da API
- `GET /health` - Health check
- `GET /docs` - Documentação interativa (Swagger)
- `POST /transcribe` - Transcrever arquivo único
- `POST /transcribe/batch` - Transcrever múltiplos arquivos
- `POST /transcribe/download` - Transcrever e baixar resultado

### 3️⃣ Docker

```bash
# Build da imagem
docker build -f docker/Dockerfile -t audio-transcriber .

# Executar container
docker run -p 8000:8000 -e OPENAI_API_KEY=sua_chave audio-transcriber

# Ou usar docker-compose
cd docker
docker-compose up
```

### 4️⃣ AWS Lambda

```bash
# Deploy usando SAM CLI
cd aws
./deploy.sh

# Ou manualmente
sam build
sam deploy --guided
```

### 5️⃣ Programaticamente

```python
# Uso tradicional (local)
from audio_transcriber import AudioTranscriber

transcriber = AudioTranscriber()
excel_file = transcriber.process_folder("/caminho/para/audios")

# Uso como serviço (API)
from audio_transcriber.api import TranscriptionService

service = TranscriptionService()
result = await service.transcribe_single_file(
    file_content=audio_bytes,
    filename="audio.mp3",
    output_format="json"
)
```

## 📊 Resultado

A ferramenta gera um arquivo Excel com duas abas:

### Aba "Transcricoes"
- **ID**: Numeração sequencial
- **Nome do arquivo**: Nome original do áudio
- **Transcrição**: Texto transcrito
- **Sucesso**: Se a transcrição foi bem-sucedida
- **Erro**: Detalhes de erro (se houver)
- **Tamanho (MB)**: Tamanho do arquivo
- **Tempo de processamento**: Tempo gasto na transcrição
- **Data da transcrição**: Quando foi processado
- **Data de modificação**: Data original do arquivo
- **Caminho completo**: Localização do arquivo

### Aba "Resumo"
- Total de arquivos processados
- Transcrições bem-sucedidas
- Número de falhas
- Taxa de sucesso
- Tamanho total processado
- Tempo total de processamento
- Data do processamento

## 🔧 Formatos Suportados

A ferramenta suporta todos os formatos aceitos pela API da OpenAI:

- **MP3** (.mp3)
- **MP4** (.mp4)
- **MPEG** (.mpeg)
- **MPGA** (.mpga)
- **M4A** (.m4a)
- **WAV** (.wav)
- **WebM** (.webm)
- **OGG** (.ogg)
- **FLAC** (.flac)

## ⚠️ Limitações

- **Tamanho máximo**: 25MB por arquivo (limitação da OpenAI)
- **Rate limiting**: Há uma pausa de 0.5s entre requisições para evitar sobrecarga
- **Custo**: Cada transcrição consome créditos da sua conta OpenAI

## 🛠️ Estrutura do Projeto

```
audio-transcriber/
├── src/
│   └── audio_transcriber/
│       ├── __init__.py           # Módulo principal
│       ├── cli.py               # Interface linha de comando
│       ├── core/                # Lógica principal
│       │   ├── __init__.py
│       │   └── transcriber.py   # Classe AudioTranscriber
│       └── api/                 # API REST
│           ├── __init__.py
│           ├── main.py          # FastAPI app
│           ├── models.py        # Modelos Pydantic
│           └── service.py       # Serviços de transcrição
├── tests/                       # Testes unitários
├── examples/                    # Exemplos de uso
├── scripts/                     # Scripts utilitários
│   ├── setup_env.py            # Configuração .env
│   ├── test_env.py             # Teste de configuração
│   ├── test_api.py             # Teste da API
│   └── test_setup.py           # Verificação completa
├── docker/                      # Configuração Docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── aws/                         # Deploy AWS Lambda
│   ├── template.yaml           # SAM template
│   ├── deploy.sh               # Script de deploy
│   └── lambda_handler.py       # Handler Lambda
├── .env.example                # Exemplo de configuração
├── .env                       # Suas configurações (não commitar)
├── pyproject.toml              # Configuração do projeto
└── README.md                   # Este arquivo
```

## 🧪 Testes e Desenvolvimento

```bash
# Testes unitários
pytest

# Teste de configuração
uv run python scripts/test_env.py

# Teste da API (servidor deve estar rodando)
uv run python scripts/test_api.py

# Formatação de código
black src tests examples
isort src tests examples

# Verificação de tipos
mypy src

# Todos os checks
uv run pytest && black --check src && isort --check src && mypy src
```

## � Deploy em Produção

### Docker
```bash
# Build e push para registry
docker build -f docker/Dockerfile -t seu-registry/audio-transcriber:latest .
docker push seu-registry/audio-transcriber:latest

# Deploy com docker-compose
cd docker
docker-compose -f docker-compose.yml up -d
```

### AWS Lambda
```bash
# Pré-requisitos: AWS CLI configurado e SAM CLI instalado
cd aws
./deploy.sh

# Ou deploy manual
sam build
sam deploy --guided --parameter-overrides OpenAIApiKey=sua_chave
```

### Kubernetes (Helm)
```bash
# Em breve: charts Helm para Kubernetes
```

## 🔍 Exemplo de Uso

```python
# Exemplo completo
from audio_transcriber import AudioTranscriber

# Configura o transcriber
transcriber = AudioTranscriber()

# Processa uma pasta com áudios
pasta = "/home/usuario/meus_audios"
excel_file = transcriber.process_folder(
    folder_path=pasta,
    output_file="transcricoes_reuniao.xlsx"
)

print(f"Transcrições salvas em: {excel_file}")
```

## 📝 Log de Atividades

A ferramenta gera logs detalhados mostrando:
- Arquivos encontrados
- Progress do processamento
- Sucessos e falhas
- Tempo de processamento
- Resumo final

## 🆘 Solução de Problemas

### Erro: "Chave da OpenAI não encontrada"
- Configure a variável de ambiente `OPENAI_API_KEY`
- Ou passe a chave como parâmetro

### Erro: "Pasta não encontrada"
- Verifique se o caminho está correto
- Use caminhos absolutos quando possível

### Erro: "Nenhum arquivo de áudio encontrado"
- Confirme se há arquivos de áudio na pasta
- Verifique se os formatos são suportados

### Erro: "Arquivo muito grande"
- O arquivo excede 25MB (limite da OpenAI)
- Considere comprimir ou dividir o arquivo

## 💡 Dicas

1. **Organize seus áudios** em uma pasta específica
2. **Use nomes descritivos** para os arquivos
3. **Monitore os custos** da API OpenAI
4. **Faça backup** das transcrições importantes
5. **Teste com poucos arquivos** primeiro

## 📄 Licença

Este projeto é fornecido como está, para uso educacional e profissional.

---

🔗 **Precisa de ajuda?** Verifique os logs de erro ou entre em contato!
