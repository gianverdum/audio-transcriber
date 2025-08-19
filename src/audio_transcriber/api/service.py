"""
API's transcription service
Abstracts the transcription logic for use in different contexts
"""

import io
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple, Union
import pandas as pd  # type: ignore[import]

from ..core import AudioTranscriber
from .models import TranscriptionResponse, BatchTranscriptionResponse


class TranscriptionService:
    """API's transcription service"""

    def __init__(self, api_key: Optional[str] = None, **config):
        """
        Initializes the transcription service

        Args:
            api_key: OpenAI API key
            **config: Additional configurations
        """
        self.transcriber = AudioTranscriber(api_key=api_key, **config)
        
    async def transcribe_single_file(
        self,
        file_content: bytes,
        filename: str,
        output_format: str = "json",
        language: Optional[str] = None,
        **options
    ) -> TranscriptionResponse:
        """
        Transcribes a single file

        Args:
            file_content: Audio file content
            filename: Name of the file
            output_format: Output format
            **options: Additional options

        Returns:
            Transcription response
        """
        start_time = time.time()
        
        try:
            # Saves temporary file
            with tempfile.NamedTemporaryFile(
                suffix=Path(filename).suffix,
                delete=False
            ) as temp_file:
                temp_file.write(file_content)
                temp_path = Path(temp_file.name)

            # Gets file information
            file_info = self.transcriber.get_file_info(temp_path)

            # Transcribes
            transcription, success, error = self.transcriber.transcribe_audio(
                temp_path, 
                language=language
            )

            # Calculates processing time
            processing_time = time.time() - start_time

            # Cleans up temporary file
            temp_path.unlink()
            
            return TranscriptionResponse(
                success=success,
                transcription=transcription if success else "",
                filename=filename,
                file_size_mb=file_info['size_mb'],
                processing_time_seconds=round(processing_time, 2),
                timestamp=datetime.now(),
                output_format=output_format,
                error=error if not success else None
            )
            
        except Exception as e:
            return TranscriptionResponse(
                success=False,
                transcription="",
                filename=filename,
                file_size_mb=0,
                processing_time_seconds=time.time() - start_time,
                timestamp=datetime.now(),
                output_format=output_format,
                error=str(e)
            )
    
    async def transcribe_batch(
        self,
        files: List[Tuple[bytes, str]],  # (content, filename)
        output_format: str = "xlsx",
        language: Optional[str] = None,
        **options
    ) -> BatchTranscriptionResponse:
        """
        Transcribes multiple files

        Args:
            files: List of tuples (content, filename)
            output_format: Output format
            **options: Additional options
            
        Returns:
            Batch transcription response
        """
        start_time = time.time()
        results = []
        successful = 0
        
        for file_content, filename in files:
            result = await self.transcribe_single_file(
                file_content, filename, output_format, language=language, **options
            )
            results.append(result)
            if result.success:
                successful += 1
        
        processing_time = time.time() - start_time
        
        return BatchTranscriptionResponse(
            success=len(results) > 0,
            total_files=len(files),
            successful_transcriptions=successful,
            failed_transcriptions=len(files) - successful,
            results=results,
            processing_time_seconds=round(processing_time, 2),
            timestamp=datetime.now(),
            output_format=output_format
        )
    
    def format_output(
        self,
        response: Union[TranscriptionResponse, BatchTranscriptionResponse],
        output_format: str
    ) -> Union[str, bytes, Dict]:
        """
        Formats the output as requested

        Args:
            response: Transcription response
            output_format: Desired format (json, txt, xlsx, csv)

        Returns:
            Formatted data
        """
        if output_format == "json":
            return response.model_dump()
        
        elif output_format == "txt":
            if isinstance(response, TranscriptionResponse):
                return response.transcription
            else:
                # For batch, concatenate all transcriptions
                texts = []
                for result in response.results:
                    if result.success:
                        texts.append(f"File: {result.filename}\n{result.transcription}\n")
                return "\n".join(texts)
        
        elif output_format in ["xlsx", "csv"]:
            return self._create_spreadsheet(response, output_format)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _create_spreadsheet(
        self,
        response: Union[TranscriptionResponse, BatchTranscriptionResponse],
        format_type: str
    ) -> bytes:
        """
        Creates Excel or CSV spreadsheet

        Args:
            response: Transcription response
            format_type: 'xlsx' or 'csv'

        Returns:
            Bytes of the spreadsheet
        """
        if isinstance(response, TranscriptionResponse):
            # Single file
            data = [{
                'file': response.filename,
                'transcription': response.transcription,
                'success': response.success,
                'error': response.error,
                'size_mb': response.file_size_mb,
                'processing_time_s': response.processing_time_seconds,
                'processing_timestamp': response.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }]
        else:
            # Batch
            data = []
            for i, result in enumerate(response.results, 1):
                data.append({
                    'id': i,
                    'file': result.filename,
                    'transcription': result.transcription,
                    'success': result.success,
                    'error': result.error,
                    'size_mb': result.file_size_mb,
                    'processing_time_s': result.processing_time_seconds,
                    'processing_timestamp': result.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        df = pd.DataFrame(data)

        # Create in-memory buffer
        buffer = io.BytesIO()
        
        if format_type == "xlsx":
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Transcriptions', index=False)

                # Add summary for batch
                if isinstance(response, BatchTranscriptionResponse):
                    summary_data = {
                        'MMetric': [
                            'Total Files',
                            'Successful Transcriptions',
                            'Failures',
                            'Success Rate (%)',
                            'Total Time (s)',
                            'Processing Timestamp'
                        ],
                        'Value': [
                            response.total_files,
                            response.successful_transcriptions,
                            response.failed_transcriptions,
                            round((response.successful_transcriptions / response.total_files) * 100, 1),
                            response.processing_time_seconds,
                            response.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Resumo', index=False)
        
        elif format_type == "csv":
            df.to_csv(buffer, index=False, encoding='utf-8')
        
        buffer.seek(0)
        return buffer.getvalue()
