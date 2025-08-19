"""
Audio Transcriber Core Module
Classe principal para transcrição de áudios usando OpenAI API
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

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """Classe principal para transcrição de áudios"""
    
    # Formatos de áudio suportados pela OpenAI
    SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
    
    def __init__(self, api_key: str = None, **config):
        """
        Inicializa o transcriber
        
        Args:
            api_key: Chave da API OpenAI (se None, busca na variável de ambiente)
            **config: Configurações adicionais (max_file_size_mb, api_delay, etc.)
        """
        # Configurações com valores padrão
        self.config = {
            'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', 25)),
            'api_delay': float(os.getenv('API_DELAY', 0.5)),
            'api_timeout': int(os.getenv('API_TIMEOUT', 30)),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'save_logs': os.getenv('SAVE_LOGS', 'false').lower() == 'true',
        }
        self.config.update(config)
        
        # Configura API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Chave da OpenAI não encontrada.\n"
                "Configure OPENAI_API_KEY no arquivo .env ou passe como parâmetro.\n"
                "Veja o arquivo .env.example para instruções."
            )
        
        # Inicializa cliente OpenAI
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=self.config['api_timeout']
        )
        self.results = []
        
        # Configura logging se necessário
        if self.config['save_logs']:
            self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging baseado nas configurações"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        
        # Remove handlers existentes
        logger.handlers.clear()
        
        # Configura formatação
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para arquivo se configurado
        if self.config['save_logs']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"audio_transcriber_{timestamp}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        logger.setLevel(log_level)
    
    def find_audio_files(self, folder_path: str) -> List[Path]:
        """
        Encontra todos os arquivos de áudio na pasta
        
        Args:
            folder_path: Caminho para a pasta com áudios
            
        Returns:
            Lista de caminhos dos arquivos de áudio
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")
        
        audio_files = []
        for file_path in folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                audio_files.append(file_path)
        
        # Ordena os arquivos por nome
        audio_files.sort(key=lambda x: x.name)
        
        logger.info(f"Encontrados {len(audio_files)} arquivos de áudio")
        return audio_files
    
    def get_file_info(self, file_path: Path) -> Dict:
        """
        Obtém informações do arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com informações do arquivo
        """
        stat = file_path.stat()
        return {
            'nome_arquivo': file_path.name,
            'caminho_completo': str(file_path),
            'tamanho_mb': round(stat.st_size / (1024 * 1024), 2),
            'data_modificacao': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def transcribe_audio(self, file_path: Path, language: Optional[str] = None) -> Tuple[str, bool, str]:
        """
        Transcreve um arquivo de áudio
        
        Args:
            file_path: Caminho do arquivo de áudio
            language: Idioma do áudio (opcional, ex: 'pt', 'en', 'portuguese')
            
        Returns:
            Tupla (transcrição, sucesso, erro)
        """
        try:
            logger.info(f"Transcrevendo: {file_path.name}")
            
            with open(file_path, "rb") as audio_file:
                # Verifica o tamanho do arquivo usando configuração
                file_size = file_path.stat().st_size
                max_size = self.config['max_file_size_mb'] * 1024 * 1024
                if file_size > max_size:
                    return "", False, f"Arquivo muito grande (>{self.config['max_file_size_mb']}MB)"
                
                # Parâmetros para a API
                api_params = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "text"
                }
                
                # Adiciona idioma se especificado
                if language:
                    api_params["language"] = language
                    logger.info(f"Idioma especificado: {language}")
                
                # Chama a API da OpenAI
                transcription = self.client.audio.transcriptions.create(**api_params)
                
                return transcription, True, ""
                
        except Exception as e:
            error_msg = f"Erro na transcrição: {str(e)}"
            logger.error(f"{file_path.name}: {error_msg}")
            return "", False, error_msg
    
    def process_folder(self, folder_path: str, output_file: str = None) -> str:
        """
        Processa todos os áudios de uma pasta
        
        Args:
            folder_path: Caminho da pasta com áudios
            output_file: Nome do arquivo Excel de saída
            
        Returns:
            Caminho do arquivo Excel gerado
        """
        # Encontra arquivos de áudio
        audio_files = self.find_audio_files(folder_path)
        
        if not audio_files:
            raise ValueError("Nenhum arquivo de áudio encontrado na pasta")
        
        # Prepara lista de resultados
        self.results = []
        
        # Processa cada arquivo
        total_files = len(audio_files)
        successful_transcriptions = 0
        
        for i, file_path in enumerate(audio_files, 1):
            logger.info(f"Processando {i}/{total_files}: {file_path.name}")
            
            # Obtém informações do arquivo
            file_info = self.get_file_info(file_path)
            
            # Transcreve o áudio
            start_time = time.time()
            transcription, success, error = self.transcribe_audio(file_path)
            processing_time = round(time.time() - start_time, 2)
            
            # Armazena resultado
            result = {
                'id': i,
                'nome_arquivo': file_info['nome_arquivo'],
                'caminho_completo': file_info['caminho_completo'],
                'tamanho_mb': file_info['tamanho_mb'],
                'data_modificacao': file_info['data_modificacao'],
                'transcricao': transcription if success else "",
                'sucesso': "Sim" if success else "Não",
                'erro': error,
                'tempo_processamento_s': processing_time,
                'data_transcricao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.results.append(result)
            
            if success:
                successful_transcriptions += 1
                logger.info(f"✓ Sucesso: {file_path.name}")
            else:
                logger.error(f"✗ Falha: {file_path.name} - {error}")
            
            # Pequena pausa para evitar rate limiting (configurável)
            time.sleep(self.config['api_delay'])
        
        # Gera arquivo Excel
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"transcricoes_{timestamp}.xlsx"
        
        excel_path = self.save_to_excel(output_file)
        
        logger.info(f"""
        ═══════════════════════════════════════
        PROCESSAMENTO CONCLUÍDO
        ═══════════════════════════════════════
        Total de arquivos: {total_files}
        Transcrições bem-sucedidas: {successful_transcriptions}
        Falhas: {total_files - successful_transcriptions}
        Arquivo Excel gerado: {excel_path}
        ═══════════════════════════════════════
        """)
        
        return excel_path
    
    def save_to_excel(self, output_file: str) -> str:
        """
        Salva os resultados em arquivo Excel
        
        Args:
            output_file: Nome do arquivo de saída
            
        Returns:
            Caminho completo do arquivo gerado
        """
        if not self.results:
            raise ValueError("Nenhum resultado para salvar")
        
        # Cria DataFrame
        df = pd.DataFrame(self.results)
        
        # Define a ordem das colunas
        columns_order = [
            'id', 'nome_arquivo', 'transcricao', 'sucesso', 'erro',
            'tamanho_mb', 'tempo_processamento_s', 'data_transcricao',
            'data_modificacao', 'caminho_completo'
        ]
        
        df = df[columns_order]
        
        # Salva no Excel com formatação
        output_path = Path(output_file).resolve()
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Aba principal com todas as transcrições
            df.to_excel(writer, sheet_name='Transcricoes', index=False)
            
            # Aba com resumo
            summary_data = {
                'Métrica': [
                    'Total de arquivos',
                    'Transcrições bem-sucedidas',
                    'Falhas',
                    'Taxa de sucesso (%)',
                    'Tamanho total (MB)',
                    'Tempo total de processamento (s)',
                    'Data do processamento'
                ],
                'Valor': [
                    len(self.results),
                    len([r for r in self.results if r['sucesso'] == 'Sim']),
                    len([r for r in self.results if r['sucesso'] == 'Não']),
                    round((len([r for r in self.results if r['sucesso'] == 'Sim']) / len(self.results)) * 100, 1),
                    round(sum(r['tamanho_mb'] for r in self.results), 2),
                    round(sum(r['tempo_processamento_s'] for r in self.results), 2),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Formatação das abas
            workbook = writer.book
            
            # Formata aba de transcrições
            transcricoes_sheet = writer.sheets['Transcricoes']
            transcricoes_sheet.column_dimensions['B'].width = 25  # nome_arquivo
            transcricoes_sheet.column_dimensions['C'].width = 50  # transcricao
            transcricoes_sheet.column_dimensions['E'].width = 30  # erro
            transcricoes_sheet.column_dimensions['J'].width = 40  # caminho_completo
            
            # Formata aba de resumo
            resumo_sheet = writer.sheets['Resumo']
            resumo_sheet.column_dimensions['A'].width = 30
            resumo_sheet.column_dimensions['B'].width = 25
        
        logger.info(f"Arquivo Excel salvo: {output_path}")
        return str(output_path)
