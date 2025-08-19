#!/usr/bin/env python3
"""
Test script to check if the .env system is working
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_dotenv():
    """Tests loading variables from .env"""
    
    print("🧪 Testing .env system")
    print("=" * 30)
    
    try:
        from dotenv import load_dotenv # type: ignore[import]
        import os
        
        # Load .env
        env_file = Path(__file__).parent.parent / ".env"
        load_dotenv(env_file)
        
        print("✅ python-dotenv installed and working")
        print(f"✅ .env file found: {env_file.exists()}")
        
        # Check some variables
        api_key = os.getenv('OPENAI_API_KEY', 'Not found')
        max_file_size = os.getenv('MAX_FILE_SIZE_MB', 'Not found')
        
        print(f"📋 OPENAI_API_KEY: {api_key[:20]}..." if api_key != 'Not found' and len(api_key) > 20 else f"📋 OPENAI_API_KEY: {api_key}")
        print(f"📋 MAX_FILE_SIZE_MB: {max_file_size}")
        
        # Test import of main module
        from audio_transcriber import AudioTranscriber
        print("✅ AudioTranscriber module imported successfully")
        
        # Check if key is properly configured
        if api_key == 'sk-proj-your_openai_key_here':
            print("⚠️  OpenAI key is still set to example value")
            print("💡 Set your real key in the .env file")
            return False
        elif api_key == 'Not found':
            print("❌ OpenAI key not found in .env")
            return False
        else:
            print("✅ OpenAI key configured in .env")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_dotenv()
    
    if success:
        print("\n🎉 .env system configured correctly!")
        print("You can now run the main tests.")
    else:
        print("\n⚠️  Set your OpenAI key in the .env file")
        print("Edit the .env file and replace 'your_openai_key_here' with your real key")
    
    sys.exit(0 if success else 1)
