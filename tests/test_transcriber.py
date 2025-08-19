"""
Unit tests for Audio Transcriber
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

 # Add the src directory to the path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber import AudioTranscriber


class TestAudioTranscriber(unittest.TestCase):
    """Tests for the AudioTranscriber class"""
    
    def setUp(self):
        """Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_api_key(self):
        """Tests initialization with API key"""
        with patch('audio_transcriber.core.transcriber.OpenAI') as mock_openai:
            transcriber = AudioTranscriber(api_key="test_key")
            self.assertEqual(transcriber.api_key, "test_key")
            mock_openai.assert_called_once_with(api_key="test_key", timeout=30)
    
    def test_init_without_api_key(self):
        """Tests initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AudioTranscriber()
    
    def test_init_with_env_api_key(self):
        """Tests initialization with API key via environment variable"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_test_key'}):
            with patch('audio_transcriber.core.transcriber.OpenAI') as mock_openai:
                transcriber = AudioTranscriber()
                self.assertEqual(transcriber.api_key, "env_test_key")
                mock_openai.assert_called_once_with(api_key="env_test_key", timeout=30)
    
    def test_find_audio_files_empty_folder(self):
        """Tests search in empty folder"""
        with patch('audio_transcriber.core.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            files = transcriber.find_audio_files(str(self.temp_path))
            self.assertEqual(len(files), 0)
    
    def test_find_audio_files_with_audio(self):
        """Tests search in folder with audio files"""
        # Create test files
        audio_files = ['test1.mp3', 'test2.wav', 'test3.txt', 'test4.ogg']
        for filename in audio_files:
            (self.temp_path / filename).touch()
        
        with patch('audio_transcriber.core.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            found_files = transcriber.find_audio_files(str(self.temp_path))
            
            # Should find only audio files (mp3, wav, ogg)
            self.assertEqual(len(found_files), 3)
            found_names = [f.name for f in found_files]
            self.assertIn('test1.mp3', found_names)
            self.assertIn('test2.wav', found_names)
            self.assertIn('test4.ogg', found_names)
            self.assertNotIn('test3.txt', found_names)
    
    def test_find_audio_files_nonexistent_folder(self):
        """Tests search in nonexistent folder"""
        with patch('audio_transcriber.core.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            with self.assertRaises(FileNotFoundError):
                transcriber.find_audio_files("/nonexistent/folder")
    
    def test_get_file_info(self):
        """Tests getting file information"""
        # Create test file
        test_file = self.temp_path / "test.mp3"
        test_content = b"fake audio content"
        test_file.write_bytes(test_content)
        
        with patch('audio_transcriber.core.transcriber.OpenAI'):
            transcriber = AudioTranscriber(api_key="test_key")
            info = transcriber.get_file_info(test_file)
            
            self.assertEqual(info['file_name'], 'test.mp3')
            self.assertEqual(info['full_path'], str(test_file))
            self.assertIsInstance(info['size_mb'], float)
            self.assertIsInstance(info['modification_date'], str)
    
    def test_supported_formats(self):
        """Tests if supported formats are correct"""
        expected_formats = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
        self.assertEqual(AudioTranscriber.SUPPORTED_FORMATS, expected_formats)
    
    @patch('audio_transcriber.core.transcriber.OpenAI')
    def test_transcribe_audio_success(self, mock_openai_class):
        """Tests successful transcription"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "Test transcription"
        
        # Create test file
        test_file = self.temp_path / "test.mp3"
        test_file.write_bytes(b"fake audio content")
        
        transcriber = AudioTranscriber(api_key="test_key")
        result, success, error = transcriber.transcribe_audio(test_file)
        
        self.assertTrue(success)
        self.assertEqual(result, "Test transcription")
        self.assertEqual(error, "")
    
    @patch('audio_transcriber.core.transcriber.OpenAI')
    def test_transcribe_audio_large_file(self, mock_openai_class):
        """Tests transcription of very large file"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Create test file
        test_file = self.temp_path / "large_test.mp3"
        test_file.write_bytes(b"fake audio content")
        
        # Create a mock version of the file that returns large size
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 26 * 1024 * 1024  # 26MB
            
            transcriber = AudioTranscriber(api_key="test_key")
            result, success, error = transcriber.transcribe_audio(test_file)
            
            self.assertFalse(success)
            self.assertEqual(result, "")
            self.assertIn("too large", error.lower())


class TestAudioTranscriberIntegration(unittest.TestCase):
    """Integration tests (require real configuration)"""
    
    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires OPENAI_API_KEY configured")
    def test_real_api_connection(self):
        """Tests real API connection (only if key is configured)"""
        transcriber = AudioTranscriber()
        self.assertIsNotNone(transcriber.client)
        self.assertIsNotNone(transcriber.api_key)


if __name__ == '__main__':
    # Configura logging para testes
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    unittest.main()
