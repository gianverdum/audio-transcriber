#!/usr/bin/env python3
"""
Exemplo de uso simples da ferramenta de transcrição
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório src ao path para importação
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber import AudioTranscriber

def exemplo_uso():
    """Exemplo básico de como usar a ferramenta"""
    
    print("🎵 Audio Transcriber - Exemplo de Uso")
    print("=" * 40)
    
    # As variáveis de ambiente são carregadas automaticamente do arquivo .env
    # Você também pode definir diretamente no código (não recomendado para produção)
    # api_key = "sua_chave_aqui"
    
    try:
        # Cria o transcriber (usando arquivo .env)
        transcriber = AudioTranscriber()
        
        # Opção com chave direta:
        # transcriber = AudioTranscriber(api_key=api_key)
        
        # Define a pasta com os áudios
        pasta_audios = input("Digite o caminho da pasta com os áudios: ").strip()
        
        if not pasta_audios:
            pasta_audios = "./audios"  # pasta padrão
        
        # Processa os áudios
        print(f"\n🎵 Iniciando transcrição dos áudios em: {pasta_audios}")
        print("⏳ Aguarde, isso pode levar alguns minutos...")
        
        excel_file = transcriber.process_folder(pasta_audios)
        
        print(f"\n✅ Concluído!")
        print(f"📊 Planilha Excel criada: {excel_file}")
        print("\nA planilha contém:")
        print("- Aba 'Transcricoes': todas as transcrições detalhadas")
        print("- Aba 'Resumo': estatísticas do processamento")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\nDicas:")
        print("1. Verifique se o arquivo .env está configurado (copie de .env.example)")
        print("2. Confirme se a chave da OpenAI está no arquivo .env")
        print("3. Confirme se a pasta de áudios existe")
        print("4. Certifique-se de que há arquivos de áudio na pasta")

if __name__ == "__main__":
    exemplo_uso()
