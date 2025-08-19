#!/usr/bin/env python3
"""
Script para testar a API do Audio Transcriber
"""

import requests
import json
import sys
from pathlib import Path
import time

def testar_api_local(base_url="http://127.0.0.1:8000"):
    """Testa a API executando localmente"""
    
    print("🧪 Testando Audio Transcriber API")
    print("=" * 40)
    print(f"🌐 Base URL: {base_url}")
    
    # Testa endpoint raiz
    print("\n1. Testando endpoint raiz...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Endpoint raiz OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("💡 Certifique-se de que o servidor está rodando:")
        print("   uv run python -m audio_transcriber.cli server")
        return False
    
    # Testa health check
    print("\n2. Testando health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check OK")
            print(f"   Status: {health_data['status']}")
            print(f"   OpenAI API: {'✅' if health_data['openai_api_available'] else '❌'}")
            print(f"   Formatos suportados: {len(health_data['supported_formats'])}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False
    
    # Testa documentação
    print("\n3. Testando documentação...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Documentação disponível")
            print(f"   URL: {base_url}/docs")
        else:
            print(f"⚠️  Documentação não acessível: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Erro ao acessar documentação: {e}")
    
    # Testa endpoint de transcrição (sem arquivo)
    print("\n4. Testando endpoint de transcrição (validação)...")
    try:
        response = requests.post(f"{base_url}/transcribe")
        if response.status_code == 422:  # Validation error esperado
            print("✅ Validação de entrada funcionando")
        else:
            print(f"⚠️  Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de validação: {e}")
    
    print("\n🎉 Testes básicos da API concluídos!")
    print(f"📖 Acesse a documentação: {base_url}/docs")
    print(f"🏥 Monitoramento: {base_url}/health")
    
    return True

def testar_com_arquivo_exemplo():
    """Testa API com arquivo de exemplo (se disponível)"""
    
    print("\n🎵 Teste com arquivo de áudio")
    print("=" * 40)
    
    # Procura por arquivos de áudio de exemplo
    exemplos = []
    for pasta in ["./audios", "./examples/audios", "../audios"]:
        pasta_path = Path(pasta)
        if pasta_path.exists():
            for ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                exemplos.extend(list(pasta_path.glob(f"*{ext}")))
    
    if not exemplos:
        print("⚠️  Nenhum arquivo de áudio encontrado para teste")
        print("💡 Coloque um arquivo de áudio em ./audios/ para testar")
        return
    
    arquivo_exemplo = exemplos[0]
    print(f"📁 Usando arquivo: {arquivo_exemplo}")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        with open(arquivo_exemplo, 'rb') as f:
            files = {'file': (arquivo_exemplo.name, f, 'audio/mpeg')}
            data = {'output_format': 'json'}
            
            print("🚀 Enviando arquivo para transcrição...")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/transcribe",
                files=files,
                data=data,
                timeout=300  # 5 minutos
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Transcrição bem-sucedida!")
                print(f"   Arquivo: {result['filename']}")
                print(f"   Sucesso: {result['success']}")
                print(f"   Tempo: {duration:.2f}s")
                if result['success']:
                    print(f"   Transcrição: {result['transcription'][:100]}...")
                else:
                    print(f"   Erro: {result['error']}")
            else:
                print(f"❌ Erro na transcrição: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro no teste com arquivo: {e}")

def main():
    """Função principal do teste"""
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://127.0.0.1:8000"
    
    # Testes básicos
    if testar_api_local(base_url):
        # Pergunta se quer testar com arquivo
        try:
            resposta = input("\n🤔 Testar com arquivo de áudio? (s/N): ").strip().lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                testar_com_arquivo_exemplo()
        except KeyboardInterrupt:
            print("\n👋 Teste finalizado")

if __name__ == "__main__":
    main()
