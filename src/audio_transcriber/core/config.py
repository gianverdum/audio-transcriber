"""
Centralized Audio Transcriber configurations
"""

import os
from typing import Optional
from dotenv import load_dotenv  # type: ignore[import-untyped]

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Centralized application settings"""
    
    # =============================================================================
    # OPENAI API SETTINGS
    # =============================================================================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # =============================================================================
    # GENERAL SETTINGS
    # =============================================================================
    DEFAULT_AUDIO_FOLDER: str = os.getenv("DEFAULT_AUDIO_FOLDER", "./audios")
    DEFAULT_OUTPUT_FOLDER: str = os.getenv("DEFAULT_OUTPUT_FOLDER", "./output")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_DELAY: float = float(os.getenv("API_DELAY", "0.5"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    
    # =============================================================================
    # API SERVER SETTINGS
    # =============================================================================
    SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    SERVER_WORKERS: int = int(os.getenv("SERVER_WORKERS", "1"))
    SERVER_RELOAD: bool = os.getenv("SERVER_RELOAD", "false").lower() == "true"
    
    # =============================================================================
    # API SETTINGS
    # =============================================================================
    API_TITLE: str = os.getenv("API_TITLE", "Audio Transcriber API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_DESCRIPTION: str = os.getenv(
        "API_DESCRIPTION", 
        "Complete API for audio transcription using OpenAI Whisper"
    )
    
    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SAVE_LOGS: bool = os.getenv("SAVE_LOGS", "false").lower() == "true"
    
    @classmethod
    def validate_openai_key(cls) -> bool:
        """Validates if OpenAI key is configured"""
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != "your_openai_key_here")
    
    @classmethod
    def get_server_url(cls) -> str:
        """Returns the complete server URL"""
        return f"http://{cls.SERVER_HOST}:{cls.SERVER_PORT}"
    
    @classmethod
    def print_server_info(cls) -> None:
        """Prints server information"""
        print(f"🚀 Starting {cls.API_TITLE}...")
        print(f"🌐 Host: {cls.SERVER_HOST}")
        print(f"🔌 Port: {cls.SERVER_PORT}")
        print(f"🔄 Reload: {'Enabled' if cls.SERVER_RELOAD else 'Disabled'}")
        print(f"👥 Workers: {cls.SERVER_WORKERS}")
        print()
        print(f"📖 Documentation: {cls.get_server_url()}/docs")
        print(f"🏥 Health Check: {cls.get_server_url()}/health")
        print()
        print("Press Ctrl+C to stop the server")


# Global settings instance
settings = Settings()
