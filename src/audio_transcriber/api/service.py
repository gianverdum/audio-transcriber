"""
Serviço de transcrição para API
Abstrai a lógica de transcrição para uso em diferentes contextos
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
    """Serviço de transcrição para API"""
    
    def __init__(self, api_key: Optional[str] = None, **config):
        """
        Inicializa o serviço de transcrição
        
        Args:
            api_key: Chave da API OpenAI
            **config: Configurações adicionais
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
        Transcreve um único arquivo
        
        Args:
            file_content: Conteúdo do arquivo de áudio
            filename: Nome do arquivo
            output_format: Formato de saída
            **options: Opções adicionais
            
        Returns:
            Resposta da transcrição
        """
        start_time = time.time()
        
        try:
            # Salva arquivo temporário
            with tempfile.NamedTemporaryFile(
                suffix=Path(filename).suffix,
                delete=False
            ) as temp_file:
                temp_file.write(file_content)
                temp_path = Path(temp_file.name)
            
            # Obtém informações do arquivo
            file_info = self.transcriber.get_file_info(temp_path)
            
            # Transcreve
            transcription, success, error = self.transcriber.transcribe_audio(
                temp_path, 
                language=language
            )
            
            # Calcula tempo de processamento
            processing_time = time.time() - start_time
            
            # Limpa arquivo temporário
            temp_path.unlink()
            
            return TranscriptionResponse(
                success=success,
                transcription=transcription if success else "",
                filename=filename,
                file_size_mb=file_info['tamanho_mb'],
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
        Transcreve múltiplos arquivos
        
        Args:
            files: Lista de tuplas (conteúdo, nome_arquivo)
            output_format: Formato de saída
            **options: Opções adicionais
            
        Returns:
            Resposta da transcrição em lote
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
        Formata a saída conforme solicitado
        
        Args:
            response: Resposta da transcrição
            output_format: Formato desejado (json, txt, xlsx, csv)
            
        Returns:
            Dados formatados
        """
        if output_format == "json":
            return response.model_dump()
        
        elif output_format == "txt":
            if isinstance(response, TranscriptionResponse):
                return response.transcription
            else:
                # Para lote, concatena todas as transcrições
                texts = []
                for result in response.results:
                    if result.success:
                        texts.append(f"Arquivo: {result.filename}\n{result.transcription}\n")
                return "\n".join(texts)
        
        elif output_format in ["xlsx", "csv"]:
            return self._create_spreadsheet(response, output_format)
        
        else:
            raise ValueError(f"Formato de saída não suportado: {output_format}")
    
    def _create_spreadsheet(
        self,
        response: Union[TranscriptionResponse, BatchTranscriptionResponse],
        format_type: str
    ) -> bytes:
        """
        Cria planilha Excel ou CSV
        
        Args:
            response: Resposta da transcrição
            format_type: 'xlsx' ou 'csv'
            
        Returns:
            Bytes da planilha
        """
        if isinstance(response, TranscriptionResponse):
            # Arquivo único
            data = [{
                'arquivo': response.filename,
                'transcricao': response.transcription,
                'sucesso': response.success,
                'erro': response.error,
                'tamanho_mb': response.file_size_mb,
                'tempo_processamento_s': response.processing_time_seconds,
                'data_processamento': response.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }]
        else:
            # Lote
            data = []
            for i, result in enumerate(response.results, 1):
                data.append({
                    'id': i,
                    'arquivo': result.filename,
                    'transcricao': result.transcription,
                    'sucesso': result.success,
                    'erro': result.error,
                    'tamanho_mb': result.file_size_mb,
                    'tempo_processamento_s': result.processing_time_seconds,
                    'data_processamento': result.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        df = pd.DataFrame(data)
        
        # Cria buffer em memória
        buffer = io.BytesIO()
        
        if format_type == "xlsx":
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Transcricoes', index=False)
                
                # Adiciona resumo para lote
                if isinstance(response, BatchTranscriptionResponse):
                    summary_data = {
                        'Métrica': [
                            'Total de arquivos',
                            'Transcrições bem-sucedidas',
                            'Falhas',
                            'Taxa de sucesso (%)',
                            'Tempo total (s)',
                            'Data do processamento'
                        ],
                        'Valor': [
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
