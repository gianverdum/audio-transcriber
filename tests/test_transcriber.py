"""
Testes unitários para Audio Transcriber
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Adiciona o diretório src ao path para importação
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber import AudioTranscriber


class TestAudioTranscriber(unittest.TestCase):
    """Testes para a classe AudioTranscriber"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_api_key(self):
        """Testa inicialização com chave API"""
        with patch('audio_transcriber.transcriber.OpenAI') as mock_openai:
            transcriber = AudioTranscriber(api_key="test_key")
            self.assertEqual(transcriber.api_key, "test_key")
            mock_openai.assert_called_once_with(api_key="test_key", timeout=30)
    
    def test_init_without_api_key(self):
        """Testa inicialização sem chave API"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AudioTranscriber()
    
    def test_init_with_env_api_key(self):
        """Testa inicialização com chave API via variável de ambiente"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_test_key'}):
            with patch('audio_transcriber.transcriber.OpenAI') as mock_openai:
                transcriber = AudioTranscriber()
                self.assertEqual(transcriber.api_key, "env_test_key")
                mock_openai.assert_called_once_with(api_key="env_test_key", timeout=30)
    
    def test_find_audio_files_empty_folder(self):
        """Testa busca em pasta vazia"""
        with patch('audio_transcriber.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            files = transcriber.find_audio_files(str(self.temp_path))
            self.assertEqual(len(files), 0)
    
    def test_find_audio_files_with_audio(self):
        """Testa busca em pasta com arquivos de áudio"""
        # Cria arquivos de teste
        audio_files = ['test1.mp3', 'test2.wav', 'test3.txt', 'test4.ogg']
        for filename in audio_files:
            (self.temp_path / filename).touch()
        
        with patch('audio_transcriber.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            found_files = transcriber.find_audio_files(str(self.temp_path))
            
            # Deve encontrar apenas os arquivos de áudio (mp3, wav, ogg)
            self.assertEqual(len(found_files), 3)
            found_names = [f.name for f in found_files]
            self.assertIn('test1.mp3', found_names)
            self.assertIn('test2.wav', found_names)
            self.assertIn('test4.ogg', found_names)
            self.assertNotIn('test3.txt', found_names)
    
    def test_find_audio_files_nonexistent_folder(self):
        """Testa busca em pasta inexistente"""
        with patch('audio_transcriber.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            with self.assertRaises(FileNotFoundError):
                transcriber.find_audio_files("/pasta/inexistente")
    
    def test_get_file_info(self):
        """Testa obtenção de informações do arquivo"""
        # Cria arquivo de teste
        test_file = self.temp_path / "test.mp3"
        test_content = b"fake audio content"
        test_file.write_bytes(test_content)
        
        with patch('audio_transcriber.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            info = transcriber.get_file_info(test_file)
            
            self.assertEqual(info['nome_arquivo'], 'test.mp3')
            self.assertEqual(info['caminho_completo'], str(test_file))
            self.assertIsInstance(info['tamanho_mb'], float)
            self.assertIsInstance(info['data_modificacao'], str)
    
    def test_supported_formats(self):
        """Testa se os formatos suportados estão corretos"""
        expected_formats = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
        self.assertEqual(AudioTranscriber.SUPPORTED_FORMATS, expected_formats)
    
    @patch('audio_transcriber.transcriber.OpenAI')
    def test_transcribe_audio_success(self, mock_openai_class):
        """Testa transcrição bem-sucedida"""
        # Configura mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "Transcrição de teste"
        
        # Cria arquivo de teste
        test_file = self.temp_path / "test.mp3"
        test_file.write_bytes(b"fake audio content")
        
        transcriber = AudioTranscriber(api_key="test_key")
        result, success, error = transcriber.transcribe_audio(test_file)
        
        self.assertTrue(success)
        self.assertEqual(result, "Transcrição de teste")
        self.assertEqual(error, "")
    
    @patch('audio_transcriber.transcriber.OpenAI')
    def test_transcribe_audio_large_file(self, mock_openai_class):
        """Testa transcrição de arquivo muito grande"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Cria arquivo de teste
        test_file = self.temp_path / "large_test.mp3"
        test_file.write_bytes(b"fake audio content")
        
        # Cria uma versão mock do arquivo que retorna tamanho grande
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 26 * 1024 * 1024  # 26MB
            
            transcriber = AudioTranscriber(api_key="test_key")
            result, success, error = transcriber.transcribe_audio(test_file)
            
            self.assertFalse(success)
            self.assertEqual(result, "")
            self.assertIn("muito grande", error.lower())


class TestAudioTranscriberIntegration(unittest.TestCase):
    """Testes de integração (requerem configuração real)"""
    
    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requer OPENAI_API_KEY configurada")
    def test_real_api_connection(self):
        """Testa conexão real com a API (apenas se a chave estiver configurada)"""
        transcriber = AudioTranscriber()
        self.assertIsNotNone(transcriber.client)
        self.assertIsNotNone(transcriber.api_key)


if __name__ == '__main__':
    # Configura logging para testes
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    unittest.main()
