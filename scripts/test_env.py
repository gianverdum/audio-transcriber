#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema de .env está funcionando
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def testar_dotenv():
    """Testa o carregamento de variáveis do .env"""
    
    print("🧪 Testando sistema .env")
    print("=" * 30)
    
    try:
        from dotenv import load_dotenv
        import os
        
        # Carrega .env
        env_file = Path(__file__).parent.parent / ".env"
        load_dotenv(env_file)
        
        print("✅ python-dotenv instalado e funcionando")
        print(f"✅ Arquivo .env encontrado: {env_file.exists()}")
        
        # Verifica algumas variáveis
        api_key = os.getenv('OPENAI_API_KEY', 'Não encontrada')
        max_file_size = os.getenv('MAX_FILE_SIZE_MB', 'Não encontrada')
        
        print(f"📋 OPENAI_API_KEY: {api_key[:20]}..." if api_key != 'Não encontrada' and len(api_key) > 20 else f"📋 OPENAI_API_KEY: {api_key}")
        print(f"📋 MAX_FILE_SIZE_MB: {max_file_size}")
        
        # Testa importação do módulo principal
        from audio_transcriber import AudioTranscriber
        print("✅ Módulo AudioTranscriber importado com sucesso")
        
        # Verifica se a chave está configurada corretamente
        if api_key == 'sk-proj-sua_chave_openai_aqui':
            print("⚠️  Chave da OpenAI ainda está com valor exemplo")
            print("💡 Configure a chave real no arquivo .env")
            return False
        elif api_key == 'Não encontrada':
            print("❌ Chave da OpenAI não encontrada no .env")
            return False
        else:
            print("✅ Chave da OpenAI configurada no .env")
            return True
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_dotenv()
    
    if sucesso:
        print("\n🎉 Sistema .env configurado corretamente!")
        print("Agora você pode executar os testes principais.")
    else:
        print("\n⚠️  Configure a chave da OpenAI no arquivo .env")
        print("Edite o arquivo .env e substitua 'sua_chave_openai_aqui' pela sua chave real")
    
    sys.exit(0 if sucesso else 1)
