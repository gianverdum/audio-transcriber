"""
Handler para AWS Lambda
Adapta a FastAPI para funcionar no Lambda usando Mangum
"""

import os
from mangum import Mangum  # type: ignore[import]
from dotenv import load_dotenv  # type: ignore[import]

# Carrega variáveis de ambiente
load_dotenv()

# Importa a aplicação FastAPI
from audio_transcriber.api.main import app  # type: ignore[import-untyped]

# Cria handler para Lambda
lambda_handler = Mangum(app, lifespan="off")

# Para testes locais
if __name__ == "__main__":
    # Simula evento Lambda para teste
    event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "body": None
    }
    context = {}
    
    result = lambda_handler(event, context)
    print(result)
