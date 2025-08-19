"""
Testes para o CLI do Audio Transcriber
"""

import unittest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adiciona o diretório src ao path para importação
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber.cli import main


class TestCLI(unittest.TestCase):
    """Testes para interface de linha de comando"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sys.argv', ['cli.py', '--help'])
    def test_help_argument(self):
        """Testa se o argumento de ajuda funciona"""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
    
    @patch('sys.argv', ['cli.py', '/pasta/inexistente'])
    @patch('audio_transcriber.cli.AudioTranscriber')
    def test_nonexistent_folder(self, mock_transcriber):
        """Testa comportamento com pasta inexistente"""
        result = main()
        self.assertEqual(result, 1)
    
    @patch('sys.argv', ['cli.py', '/tmp'])
    @patch('audio_transcriber.cli.AudioTranscriber')
    def test_basic_usage(self, mock_transcriber_class):
        """Testa uso básico do CLI"""
        # Configura mock
        mock_transcriber = MagicMock()
        mock_transcriber_class.return_value = mock_transcriber
        mock_transcriber.process_folder.return_value = "test_output.xlsx"
        
        with patch('pathlib.Path.exists', return_value=True):
            result = main()
            
        self.assertEqual(result, 0)
        mock_transcriber.process_folder.assert_called_once()


if __name__ == '__main__':
    unittest.main()
