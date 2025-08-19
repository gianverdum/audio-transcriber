"""
Tests for the Audio Transcriber CLI
"""

import unittest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

 # Add the src directory to the path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber.cli import main


class TestCLI(unittest.TestCase):
    """Tests for command line interface"""
    
    def setUp(self):
        """Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sys.argv', ['cli.py', '--help'])
    def test_help_argument(self):
        """Tests if the help argument works"""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
    
    @patch('sys.argv', ['cli.py', 'transcribe', '/nonexistent/folder'])
    @patch('audio_transcriber.cli.AudioTranscriber')
    def test_nonexistent_folder(self, mock_transcriber):
        """Tests behavior with nonexistent folder"""
        result = main()
        self.assertEqual(result, 1)
    
    @patch('sys.argv', ['cli.py', 'transcribe', '/tmp'])
    @patch('audio_transcriber.cli.AudioTranscriber')
    def test_basic_usage(self, mock_transcriber_class):
        """Tests basic CLI usage"""
        # Setup mock
        mock_transcriber = MagicMock()
        mock_transcriber_class.return_value = mock_transcriber
        mock_transcriber.process_folder.return_value = "test_output.xlsx"
        
        with patch('pathlib.Path.exists', return_value=True):
            result = main()
            
        self.assertEqual(result, 0)
        mock_transcriber.process_folder.assert_called_once()


if __name__ == '__main__':
    unittest.main()
