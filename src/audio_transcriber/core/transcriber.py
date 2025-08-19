"""
Audio Transcriber Core Module
Main class for audio transcription using OpenAI API
"""

import os
import pandas as pd  # type: ignore[import]
from openai import OpenAI  # type: ignore[import]
from pathlib import Path
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging
from dotenv import load_dotenv  # type: ignore[import]

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """Main class for audio transcription"""

    # Supported audio formats by OpenAI
    SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
    
    def __init__(self, api_key: str = None, **config):
        """
        Initializes the transcriber
        
        Args:
            api_key: OpenAI API key (if None, it looks in the environment variable)
            **config: Additional configurations (max_file_size_mb, api_delay, etc.)
        """
        # Default configuration values
        self.config = {
            'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', 25)),
            'api_delay': float(os.getenv('API_DELAY', 0.5)),
            'api_timeout': int(os.getenv('API_TIMEOUT', 30)),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'save_logs': os.getenv('SAVE_LOGS', 'false').lower() == 'true',
        }
        self.config.update(config)

        # Sets API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found.\n"
                "Set OPENAI_API_KEY in the .env file or pass it as a parameter.\n"
                "See the .env.example file for instructions."
            )

        # Initializes OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=self.config['api_timeout']
        )
        self.results = []

        # Logging configuration if needed
        if self.config['save_logs']:
            self._setup_logging()
    
    def _setup_logging(self):
        """Configures logging based on the settings"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)

        # Remove existing handlers
        logger.handlers.clear()

        # Sets formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if configured
        if self.config['save_logs']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"audio_transcriber_{timestamp}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        logger.setLevel(log_level)
    
    def find_audio_files(self, folder_path: str) -> List[Path]:
        """
        Finds all audio files in the folder

        Args:
            folder_path: Path to the folder with audio files

        Returns:
            List of paths to audio files
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        audio_files = []
        for file_path in folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                audio_files.append(file_path)

        # Sorts files by name
        audio_files.sort(key=lambda x: x.name)

        logger.info(f"Found {len(audio_files)} audio files")
        return audio_files
    
    def get_file_info(self, file_path: Path) -> Dict:
        """
        Obtains file information

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        stat = file_path.stat()
        return {
            'file_name': file_path.name,
            'full_path': str(file_path),
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modification_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def transcribe_audio(self, file_path: Path, language: Optional[str] = None) -> Tuple[str, bool, str]:
        """
        Transcribes an audio file

        Args:
            file_path: Audio file path
            language: Audio language (optional, e.g., 'pt', 'en', 'portuguese')

        Returns:
            Tuple (transcription, success, error)
        """
        try:
            logger.info(f"Transcribing: {file_path.name}")

            with open(file_path, "rb") as audio_file:
                # Checks file size against configuration
                file_size = file_path.stat().st_size
                max_size = self.config['max_file_size_mb'] * 1024 * 1024
                if file_size > max_size:
                    return "", False, f"File too large (>{self.config['max_file_size_mb']}MB)"

                # API parameters
                api_params = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "text"
                }

                # Adds language if specified
                if language:
                    api_params["language"] = language
                    logger.info(f"Specified language: {language}")

                # Calls the OpenAI API
                transcription = self.client.audio.transcriptions.create(**api_params)
                
                return transcription, True, ""
                
        except Exception as e:
            error_msg = f"Error in transcription: {str(e)}"
            logger.error(f"{file_path.name}: {error_msg}")
            return "", False, error_msg
    
    def process_folder(self, folder_path: str, output_file: str = None) -> str:
        """
        Processes all audio files in a folder

        Args:
            folder_path: Path to the folder with audio files
            output_file: Name of the output Excel file

        Returns:
            Path to the generated Excel file
        """
        # Finds audio files
        audio_files = self.find_audio_files(folder_path)
        
        if not audio_files:
            raise ValueError("No audio files found in the folder")

        # Prepares results list
        self.results = []

        # Processes each file
        total_files = len(audio_files)
        successful_transcriptions = 0
        
        for i, file_path in enumerate(audio_files, 1):
            logger.info(f"Processing {i}/{total_files}: {file_path.name}")

            # Obtains file information
            file_info = self.get_file_info(file_path)

            # Transcribes the audio
            start_time = time.time()
            transcription, success, error = self.transcribe_audio(file_path)
            processing_time = round(time.time() - start_time, 2)

            # Stores result
            result = {
                'id': i,
                'file_name': file_info['file_name'],
                'full_path': file_info['full_path'],
                'size_mb': file_info['size_mb'],
                'modification_date': file_info['modification_date'],
                'transcription': transcription if success else "",
                'success': "Yes" if success else "No",
                'error': error,
                'processing_time_s': processing_time,
                'transcription_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.results.append(result)
            
            if success:
                successful_transcriptions += 1
                logger.info(f"✓ Success: {file_path.name}")
            else:
                logger.error(f"✗ Failure: {file_path.name} - {error}")

            # Small pause to avoid rate limiting (configurable)
            time.sleep(self.config['api_delay'])

        # Generates Excel file
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"transcriptions_{timestamp}.xlsx"

        excel_path = self.save_to_excel(output_file)
        
        logger.info(f"""
        ═══════════════════════════════════════
        PROCESS FINISHED
        ═══════════════════════════════════════
        Total files: {total_files}
        Successful transcriptions: {successful_transcriptions}
        Failures: {total_files - successful_transcriptions}
        Generated Excel file: {excel_path}
        ═══════════════════════════════════════
        """)
        
        return excel_path
    
    def save_to_excel(self, output_file: str) -> str:
        """
        Saves the results to an Excel file

        Args:
            output_file: Name of the output file

        Returns:
            Full path of the generated file
        """
        if not self.results:
            raise ValueError("No results to save")

        # Creates DataFrame
        df = pd.DataFrame(self.results)

        # Define the order of the columns
        columns_order = [
            'id', 'file_name', 'transcription', 'success', 'error',
            'size_mb', 'processing_time_s', 'transcription_date',
            'modification_date', 'full_path'
        ]
        
        df = df[columns_order]

        # Saves to Excel with formatting
        output_path = Path(output_file).resolve()
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main sheet with all transcriptions
            df.to_excel(writer, sheet_name='Transcriptions', index=False)

            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total files',
                    'Successful transcriptions',
                    'Failures',
                    'Success rate (%)',
                    'Total size (MB)',
                    'Total processing time (s)',
                    'Processing date'
                ],
                'Value': [
                    len(self.results),
                    len([r for r in self.results if r['success'] == 'Yes']),
                    len([r for r in self.results if r['success'] == 'No']),
                    round((len([r for r in self.results if r['success'] == 'Yes']) / len(self.results)) * 100, 1),
                    round(sum(r['size_mb'] for r in self.results), 2),
                    round(sum(r['processing_time_s'] for r in self.results), 2),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Formatting the sheets
            workbook = writer.book

            # Formats transcription sheet
            transcriptions_sheet = writer.sheets['Transcriptions']
            transcriptions_sheet.column_dimensions['B'].width = 25  # file_name
            transcriptions_sheet.column_dimensions['C'].width = 50  # transcription
            transcriptions_sheet.column_dimensions['E'].width = 30  # error
            transcriptions_sheet.column_dimensions['J'].width = 40  # full_path

            # Formats summary sheet
            summary_sheet = writer.sheets['Summary']
            summary_sheet.column_dimensions['A'].width = 30
            summary_sheet.column_dimensions['B'].width = 25

        logger.info(f"Excel file saved: {output_path}")
        return str(output_path)
