#!/usr/bin/env python3
"""
Test script to verify installation and configuration
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Checks if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import openai # type: ignore[import]
        print("✅ OpenAI installed")
    except ImportError:
        print("❌ OpenAI not found. Run: pip install openai")
        return False
    
    try:
        import pandas # type: ignore[import]
        print("✅ Pandas installed")
    except ImportError:
        print("❌ Pandas not found. Run: pip install pandas")
        return False
    
    try:
        import openpyxl # type: ignore[import]
        print("✅ OpenPyXL installed")
    except ImportError:
        print("❌ OpenPyXL not found. Run: pip install openpyxl")
        return False
    
    return True

def check_openai_key():
    """Checks if the OpenAI key is configured"""
    print("\n🔑 Checking OpenAI key...")
    
    # Load .env first
    try:
        from dotenv import load_dotenv # type: ignore[import]
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, trying direct environment variable")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI key not found")
        print("Configure it in the .env file or as an environment variable")
        print("Example .env: OPENAI_API_KEY='your_key_here'")
        return False
    
    if api_key.startswith('sk-'):
        print("✅ OpenAI key configured")
        return True
    else:
        print("⚠️  Key format seems incorrect (should start with 'sk-')")
        return False

def check_project_structure():
    """Checks if the project files are present"""
    print("\n📁 Checking project structure...")
    
    required_files = [
        'src/audio_transcriber/__init__.py',
        'src/audio_transcriber/core/transcriber.py',
        'src/audio_transcriber/cli.py',
        'pyproject.toml',
        '.env.example',
        'README.md'
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            all_present = False
    
    return all_present

def test_import():
    """Tests if the main module can be imported"""
    print("\n📦 Testing module import...")
    
    try:
        # Add src to path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from audio_transcriber import AudioTranscriber
        print("✅ AudioTranscriber module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing: {e}")
        return False

def create_test_folders():
    """Creates example folders for testing"""
    print("\n📂 Creating test structure...")
    
    try:
        # Create example folders
        Path("./audios").mkdir(exist_ok=True)
        Path("./output").mkdir(exist_ok=True)
        
        print("✅ Folders created:")
        print("  - ./audios (put your audio files here)")
        print("  - ./output (Excel spreadsheets will be saved here)")
        
        return True
    except Exception as e:
        print(f"❌ Error creating folders: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 CONFIGURATION TEST - Audio Transcriber")
    print("=" * 50)
    
    # List of checks
    checks = [
        ("Dependencies", check_dependencies),
        ("OpenAI Key", check_openai_key),
        ("Project Structure", check_project_structure),
        ("Module Import", test_import),
        ("Folder Creation", create_test_folders)
    ]
    
    results = []
    
    for name, func in checks:
        result = func()
        results.append((name, result))
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    successes = 0
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name:.<30} {status}")
        if success:
            successes += 1
    
    print("\n" + "=" * 50)
    
    if successes == len(results):
        print("🎉 ALL TESTS PASSED!")
        print("Your installation is ready to use.")
        print("\nTo get started:")
        print("1. Put your audio files in the './audios' folder")
        print("2. Run: python example_usage.py")
    else:
        print(f"⚠️  {len(results) - successes} test(s) failed")
        print("Fix the issues before using the tool.")
    
    return 0 if successes == len(results) else 1

if __name__ == "__main__":
    exit(main())
