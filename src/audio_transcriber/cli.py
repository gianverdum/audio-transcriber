#!/usr/bin/env python3
"""
CLI para Audio Transcriber
Command line interface for audio transcription
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv  # type: ignore[import]

# Load environment variables from .env file
load_dotenv()

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber.core.transcriber import AudioTranscriber
from audio_transcriber.core.config import settings

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function of the CLI"""
    parser = argparse.ArgumentParser(
        description='Audio Transcriber - Audio transcription using OpenAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  
  Local transcription:
    %(prog)s transcribe ./audios
    %(prog)s transcribe ./audios -o my_transcriptions.xlsx
    %(prog)s transcribe ./audios -k your_openai_key
  
  API server:
    %(prog)s server --host 0.0.0.0 --port 8000
    %(prog)s server --reload
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Command transcribe (original behavior)
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe files locally')
    transcribe_parser.add_argument(
        'folder',
        help='Folder containing audio files'
    )
    transcribe_parser.add_argument(
        '-o', '--output',
        help='Name of the output Excel file'
    )
    transcribe_parser.add_argument(
        '-k', '--api-key',
        help='OpenAI API key (or use OPENAI_API_KEY)'
    )
    transcribe_parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Verbose mode (more details in log)'
    )

    # Command server (new functionality)
    server_parser = subparsers.add_parser('server', help='Run API server')
    server_parser.add_argument(
        '--host',
        default=settings.SERVER_HOST,
        help=f'Host for the server (default: {settings.SERVER_HOST}, from .env: SERVER_HOST)'
    )
    server_parser.add_argument(
        '--port',
        type=int,
        default=settings.SERVER_PORT,
        help=f'Port for the server (default: {settings.SERVER_PORT}, from .env: SERVER_PORT)'
    )
    server_parser.add_argument(
        '--reload',
        action='store_true',
        default=settings.SERVER_RELOAD,
        help=f'Enable auto-reload for development (default: {settings.SERVER_RELOAD}, from .env: SERVER_RELOAD)'
    )
    server_parser.add_argument(
        '--workers',
        type=int,
        default=settings.SERVER_WORKERS,
        help=f'Number of workers (default: {settings.SERVER_WORKERS}, from .env: SERVER_WORKERS)'
    )
    
    args = parser.parse_args()

    # If no command was specified, assume transcribe for compatibility
    if not args.command:
        # Check if the first argument looks like a folder
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            # Simulate transcribe command
            transcribe_args = argparse.Namespace()
            transcribe_args.folder = sys.argv[1]
            transcribe_args.output = None
            transcribe_args.api_key = None
            transcribe_args.verbose = False

            # Process remaining arguments
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

    # Configure log level if verbose
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute appropriate command
    if args.command == 'transcribe':
        return _handle_transcribe(args)
    elif args.command == 'server':
        return _handle_server(args)
    else:
        parser.print_help()
        return 1


def _handle_transcribe(args):
    """Handles transcribe command"""
    try:
        # Create the transcriber
        print("🎵 Initializing Audio Transcriber...")
        transcriber = AudioTranscriber(api_key=args.api_key)

        # Validate input folder
        folder_path = Path(args.folder)
        if not folder_path.exists():
            logger.error(f"Folder not found: {args.folder}")
            return 1

        # Process the folder
        print(f"📁 Processing folder: {folder_path}")
        excel_file = transcriber.process_folder(args.folder, args.output)

        print(f"\n🎉 Transcriptions completed!")
        print(f"📊 Excel spreadsheet generated: {excel_file}")

        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


def _handle_server(args):
    """Handles server command"""
    try:
        print("🚀 Starting Audio Transcriber API Server...")
        print(f"🌐 Host: {args.host}")
        print(f"🔌 Port: {args.port}")
        print(f"🔄 Reload: {'Enabled' if args.reload else 'Disabled'}")
        print(f"👥 Workers: {args.workers}")
        print()
        print(f"📖 Documentation: http://{args.host}:{args.port}/docs")
        print(f"🏥 Health Check: http://{args.host}:{args.port}/health")
        print()
        print("Press Ctrl+C to stop the server")

        # Import and run server using centralized settings
        from .api.main import run_local
        run_local(
            host=args.host, 
            port=args.port, 
            reload=args.reload,
            workers=args.workers
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
