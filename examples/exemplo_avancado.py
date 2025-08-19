#!/usr/bin/env python3
"""
Exemplo avançado de uso da ferramenta de transcrição
Demonstra uso programático com configurações customizadas
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório src ao path para importação
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber import AudioTranscriber

def configurar_logging():
    """Configura logging customizado"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'transcricao_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

def exemplo_avancado():
    """Exemplo com uso mais avançado da ferramenta"""
    
    print("🎵 Audio Transcriber - Exemplo Avançado")
    print("=" * 45)
    
    # Configura logging
    configurar_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Configurações (agora vêm do arquivo .env)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  Configure OPENAI_API_KEY no arquivo .env antes de continuar")
            print("💡 Copie .env.example para .env e configure suas credenciais")
            return
        
        # Cria o transcriber com configurações customizadas
        transcriber = AudioTranscriber(
            # Configurações opcionais podem sobrescrever as do .env
            max_file_size_mb=30,  # Exemplo: arquivo maior que o padrão
            api_delay=1.0,        # Exemplo: pausa maior entre requisições
            save_logs=True        # Salva logs em arquivo
        )
        
        # Define pastas
        pasta_audios = "./audios"
        pasta_saida = "./output"
        
        # Cria pastas se não existirem
        Path(pasta_audios).mkdir(exist_ok=True)
        Path(pasta_saida).mkdir(exist_ok=True)
        
        # Verifica se há arquivos
        audio_files = transcriber.find_audio_files(pasta_audios)
        if not audio_files:
            print(f"❌ Nenhum arquivo de áudio encontrado em {pasta_audios}")
            print("Coloque alguns arquivos de áudio na pasta e tente novamente.")
            return
        
        print(f"📁 Encontrados {len(audio_files)} arquivos de áudio")
        
        # Lista os arquivos encontrados
        print("\n📋 Arquivos que serão processados:")
        for i, file_path in enumerate(audio_files, 1):
            file_info = transcriber.get_file_info(file_path)
            print(f"  {i:2d}. {file_info['nome_arquivo']} ({file_info['tamanho_mb']} MB)")
        
        # Confirma processamento
        resposta = input("\n🤔 Continuar com a transcrição? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("⏹️  Processamento cancelado")
            return
        
        # Nome do arquivo de saída
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(pasta_saida) / f"transcricoes_avancado_{timestamp}.xlsx"
        
        # Processa com medição de tempo
        inicio = datetime.now()
        print(f"\n🚀 Iniciando processamento às {inicio.strftime('%H:%M:%S')}")
        
        excel_file = transcriber.process_folder(pasta_audios, str(output_file))
        
        fim = datetime.now()
        duracao = fim - inicio
        
        # Relatório final
        print(f"\n🎉 Processamento concluído!")
        print(f"⏱️  Tempo total: {duracao}")
        print(f"📊 Planilha Excel: {excel_file}")
        
        # Estatísticas dos resultados
        if transcriber.results:
            sucessos = len([r for r in transcriber.results if r['sucesso'] == 'Sim'])
            falhas = len(transcriber.results) - sucessos
            taxa_sucesso = (sucessos / len(transcriber.results)) * 100
            
            print(f"\n📈 Estatísticas:")
            print(f"   Sucessos: {sucessos}")
            print(f"   Falhas: {falhas}")
            print(f"   Taxa de sucesso: {taxa_sucesso:.1f}%")
            
            if falhas > 0:
                print(f"\n❌ Arquivos com falha:")
                for resultado in transcriber.results:
                    if resultado['sucesso'] == 'Não':
                        print(f"   - {resultado['nome_arquivo']}: {resultado['erro']}")
        
        logger.info("Processamento avançado concluído com sucesso")
        
    except KeyboardInterrupt:
        print("\n⚠️  Processamento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no exemplo avançado: {e}")
        print(f"❌ Erro: {e}")

def exemplo_processamento_lote():
    """Exemplo de processamento de múltiplas pastas"""
    
    print("\n🗂️  Exemplo: Processamento em Lote")
    print("=" * 40)
    
    pastas_audio = [
        "./audios/reuniao1",
        "./audios/reuniao2", 
        "./audios/entrevistas"
    ]
    
    try:
        transcriber = AudioTranscriber()
        
        for pasta in pastas_audio:
            if Path(pasta).exists():
                print(f"\n📁 Processando: {pasta}")
                
                nome_pasta = Path(pasta).name
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"transcricoes_{nome_pasta}_{timestamp}.xlsx"
                
                excel_file = transcriber.process_folder(pasta, output_file)
                print(f"✅ Concluído: {excel_file}")
            else:
                print(f"⚠️  Pasta não encontrada: {pasta}")
                
    except Exception as e:
        print(f"❌ Erro no processamento em lote: {e}")

if __name__ == "__main__":
    exemplo_avancado()
    
    # Pergunta se quer executar exemplo de lote
    resposta = input("\n🤔 Executar exemplo de processamento em lote? (s/N): ").strip().lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        exemplo_processamento_lote()
