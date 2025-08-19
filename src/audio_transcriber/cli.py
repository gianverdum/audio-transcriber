#!/usr/bin/env python3
"""
CLI para Audio Transcriber
Interface de linha de comando para transcrição de áudios
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv  # type: ignore[import]

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório src ao path para importação
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber.core.transcriber import AudioTranscriber

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description='Audio Transcriber - Transcrição de áudios usando OpenAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos disponíveis:
  
  Transcrição local:
    %(prog)s transcribe ./audios
    %(prog)s transcribe ./audios -o minhas_transcricoes.xlsx
    %(prog)s transcribe ./audios -k sua_chave_openai
  
  Servidor API:
    %(prog)s server --host 0.0.0.0 --port 8000
    %(prog)s server --reload
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando transcribe (comportamento original)
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcrever arquivos localmente')
    transcribe_parser.add_argument(
        'folder', 
        help='Pasta contendo os arquivos de áudio'
    )
    transcribe_parser.add_argument(
        '-o', '--output', 
        help='Nome do arquivo Excel de saída'
    )
    transcribe_parser.add_argument(
        '-k', '--api-key', 
        help='Chave da API OpenAI (ou use OPENAI_API_KEY)'
    )
    transcribe_parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Modo verboso (mais detalhes no log)'
    )
    
    # Comando server (nova funcionalidade)
    server_parser = subparsers.add_parser('server', help='Executar servidor API')
    server_parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host para o servidor (default: 127.0.0.1)'
    )
    server_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Porta para o servidor (default: 8000)'
    )
    server_parser.add_argument(
        '--reload',
        action='store_true',
        help='Ativar auto-reload para desenvolvimento'
    )
    server_parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Número de workers (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Se nenhum comando foi especificado, assume transcribe para compatibilidade
    if not args.command:
        # Verifica se o primeiro argumento parece uma pasta
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            # Simula comando transcribe
            transcribe_args = argparse.Namespace()
            transcribe_args.folder = sys.argv[1]
            transcribe_args.output = None
            transcribe_args.api_key = None
            transcribe_args.verbose = False
            
            # Processa argumentos restantes
            for i, arg in enumerate(sys.argv[2:], 2):
                if arg in ['-o', '--output'] and i+1 < len(sys.argv):
                    transcribe_args.output = sys.argv[i+1]
                elif arg in ['-k', '--api-key'] and i+1 < len(sys.argv):
                    transcribe_args.api_key = sys.argv[i+1]
                elif arg in ['-v', '--verbose']:
                    transcribe_args.verbose = True
            
            return _handle_transcribe(transcribe_args)
        else:
            parser.print_help()
            return 1
    
    # Configura nível de log se verbose
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Executa comando apropriado
    if args.command == 'transcribe':
        return _handle_transcribe(args)
    elif args.command == 'server':
        return _handle_server(args)
    else:
        parser.print_help()
        return 1


def _handle_transcribe(args):
    """Lida com comando de transcrição"""
    try:
        # Cria o transcriber
        print("🎵 Inicializando Audio Transcriber...")
        transcriber = AudioTranscriber(api_key=args.api_key)
        
        # Valida pasta de entrada
        folder_path = Path(args.folder)
        if not folder_path.exists():
            logger.error(f"Pasta não encontrada: {args.folder}")
            return 1
        
        # Processa a pasta
        print(f"📁 Processando pasta: {folder_path}")
        excel_file = transcriber.process_folder(args.folder, args.output)
        
        print(f"\n🎉 Transcrições concluídas!")
        print(f"📊 Planilha Excel gerada: {excel_file}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Processamento interrompido pelo usuário")
        return 130
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


def _handle_server(args):
    """Lida com comando de servidor"""
    try:
        print("🚀 Iniciando Audio Transcriber API Server...")
        print(f"🌐 Host: {args.host}")
        print(f"🔌 Porta: {args.port}")
        print(f"🔄 Reload: {'Ativado' if args.reload else 'Desativado'}")
        print(f"👥 Workers: {args.workers}")
        print()
        print(f"📖 Documentação: http://{args.host}:{args.port}/docs")
        print(f"🏥 Health Check: http://{args.host}:{args.port}/health")
        print()
        print("Pressione Ctrl+C para parar o servidor")
        
        # Importa e executa servidor
        from .api.main import run_local
        run_local(host=args.host, port=args.port, reload=args.reload)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Servidor parado pelo usuário")
        return 0
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
