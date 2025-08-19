#!/usr/bin/env python3
"""
Script to test the Audio Transcriber API
"""

import requests # type: ignore[import]
import json
import sys
from pathlib import Path
import time

def test_local_api(base_url="http://127.0.0.1:8000"):
    """Tests the API running locally"""
    
    print("🧪 Testing Audio Transcriber API")
    print("=" * 40)
    print(f"🌐 Base URL: {base_url}")
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the server is running:")
        print("   uv run python -m audio_transcriber.cli server")
        return False
    
    # Test health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check OK")
            print(f"   Status: {health_data['status']}")
            print(f"   OpenAI API: {'✅' if health_data['openai_api_available'] else '❌'}")
            print(f"   Supported formats: {len(health_data['supported_formats'])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test documentation
    print("\n3. Testing documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Documentation available")
            print(f"   URL: {base_url}/docs")
        else:
            print(f"⚠️  Documentation not accessible: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error accessing documentation: {e}")
    
    # Test transcription endpoint (no file)
    print("\n4. Testing transcription endpoint (validation)...")
    try:
        response = requests.post(f"{base_url}/transcribe")
        if response.status_code == 422:  # Expected validation error
            print("✅ Input validation working")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Validation test error: {e}")
    
    print("\n🎉 Basic API tests completed!")
    print(f"📖 Access documentation: {base_url}/docs")
    print(f"🏥 Monitoring: {base_url}/health")
    
    return True

def test_with_example_file():
    """Tests API with example audio file (if available)"""
    
    print("\n🎵 Test with audio file")
    print("=" * 40)
    
    # Search for example audio files
    examples = []
    for folder in ["./audios", "./examples/audios", "../audios"]:
        folder_path = Path(folder)
        if folder_path.exists():
            for ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                examples.extend(list(folder_path.glob(f"*{ext}")))
    
    if not examples:
        print("⚠️  No audio file found for testing")
        print("💡 Place an audio file in ./audios/ to test")
        return
    
    example_file = examples[0]
    print(f"📁 Using file: {example_file}")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        with open(example_file, 'rb') as f:
            files = {'file': (example_file.name, f, 'audio/mpeg')}
            data = {'output_format': 'json'}
            
            print("🚀 Sending file for transcription...")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/transcribe",
                files=files,
                data=data,
                timeout=300  # 5 minutes
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Transcription successful!")
                print(f"   File: {result['filename']}")
                print(f"   Success: {result['success']}")
                print(f"   Time: {duration:.2f}s")
                if result['success']:
                    print(f"   Transcription: {result['transcription'][:100]}...")
                else:
                    print(f"   Error: {result['error']}")
            else:
                print(f"❌ Transcription error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error in file test: {e}")

def main():
    """Main test function"""
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://127.0.0.1:8000"
    
    # Basic tests
    if test_local_api(base_url):
        # Ask if want to test with file
        try:
            answer = input("\n🤔 Test with audio file? (y/N): ").strip().lower()
            if answer in ['s', 'sim', 'y', 'yes']:
                test_with_example_file()
        except KeyboardInterrupt:
            print("\n👋 Test finished")

if __name__ == "__main__":
    main()
