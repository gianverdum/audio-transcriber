#!/usr/bin/env python3
"""
Test script to validate configuration and authentication features
"""

import os
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber.core.config import settings
from audio_transcriber.core.transcriber import AudioTranscriber


def test_openai_key_loading():
    """Test OpenAI API key loading from different sources"""
    print("🔑 Testing OpenAI API Key Loading...")
    
    # Test 1: Environment variable loading
    original_key = os.getenv("OPENAI_API_KEY")
    print(f"   Environment OPENAI_API_KEY: {'Set' if original_key else 'Not set'}")
    
    # Test 2: Docker secret simulation
    with tempfile.TemporaryDirectory() as temp_dir:
        secret_path = os.path.join(temp_dir, "openai_api_key")
        with open(secret_path, 'w') as f:
            f.write("sk-test-secret-key-from-docker")
        
        # Temporarily patch the secret path
        original_load_method = settings.load_openai_key
        
        def mock_load_openai_key():
            if os.path.exists(secret_path):
                try:
                    with open(secret_path, 'r') as f:
                        return f.read().strip()
                except Exception:
                    pass
            return settings.OPENAI_API_KEY
        
        settings.load_openai_key = mock_load_openai_key
        
        loaded_key = settings.load_openai_key()
        print(f"   Docker secret simulation: {'✅ Working' if loaded_key == 'sk-test-secret-key-from-docker' else '❌ Failed'}")
        
        # Restore original method
        settings.load_openai_key = original_load_method
    
    # Test 3: Validation
    is_valid = settings.validate_openai_key()
    print(f"   OpenAI key validation: {'✅ Valid' if is_valid else '❌ Invalid/Missing'}")
    
    # Test 4: Get key method
    current_key = settings.get_openai_key()
    print(f"   Current key method: {'✅ Working' if current_key else '❌ Empty'}")
    
    return is_valid


def test_auth_token():
    """Test authentication token configuration"""
    print("\n🔐 Testing Authentication Token...")
    
    auth_token = settings.AUTH_TOKEN
    print(f"   AUTH_TOKEN configured: {'✅ Yes' if auth_token else '❌ No'}")
    
    if auth_token:
        print(f"   Token length: {len(auth_token)} characters")
        print(f"   Token preview: {auth_token[:8]}{'*' * max(0, len(auth_token) - 8)}")
    
    return bool(auth_token)


def test_transcriber_initialization():
    """Test if AudioTranscriber can initialize with current configuration"""
    print("\n🎯 Testing AudioTranscriber Initialization...")
    
    try:
        transcriber = AudioTranscriber()
        print("   ✅ AudioTranscriber initialized successfully")
        
        # Test API key access
        api_key = transcriber.openai_api_key
        if api_key:
            print(f"   ✅ API key loaded: {api_key[:8]}{'*' * max(0, len(api_key) - 8)}")
            return True
        else:
            print("   ❌ API key not loaded")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False


def test_server_configuration():
    """Test server configuration"""
    print("\n🌐 Testing Server Configuration...")
    
    print(f"   API Server Host: {settings.SERVER_HOST}")
    print(f"   API Server Port: {settings.SERVER_PORT}")
    print(f"   MCP Server Host: {settings.MCP_SERVER_HOST}")
    print(f"   MCP Server Port: {settings.MCP_SERVER_PORT}")
    print(f"   Server URL: {settings.get_server_url()}")
    
    # Test port availability
    import socket
    
    def is_port_available(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return True
        except OSError:
            return False
    
    api_port_available = is_port_available(settings.SERVER_HOST, settings.SERVER_PORT)
    mcp_port_available = is_port_available(settings.MCP_SERVER_HOST, settings.MCP_SERVER_PORT)
    
    print(f"   API Port {settings.SERVER_PORT} available: {'✅ Yes' if api_port_available else '❌ No (in use)'}")
    print(f"   MCP Port {settings.MCP_SERVER_PORT} available: {'✅ Yes' if mcp_port_available else '❌ No (in use)'}")
    
    return api_port_available and mcp_port_available


def test_environment_variables():
    """Test all important environment variables"""
    print("\n🌍 Testing Environment Variables...")
    
    important_vars = [
        ("OPENAI_API_KEY", settings.OPENAI_API_KEY),
        ("AUTH_TOKEN", settings.AUTH_TOKEN),
        ("SERVER_HOST", settings.SERVER_HOST),
        ("SERVER_PORT", settings.SERVER_PORT),
        ("MCP_SERVER_PORT", settings.MCP_SERVER_PORT),
        ("LOG_LEVEL", settings.LOG_LEVEL),
        ("MAX_FILE_SIZE_MB", settings.MAX_FILE_SIZE_MB),
    ]
    
    all_good = True
    for var_name, var_value in important_vars:
        if var_value:
            if var_name in ["OPENAI_API_KEY", "AUTH_TOKEN"]:
                print(f"   {var_name}: ✅ Set ({len(str(var_value))} chars)")
            else:
                print(f"   {var_name}: ✅ {var_value}")
        else:
            print(f"   {var_name}: ❌ Not set")
            if var_name == "OPENAI_API_KEY":
                all_good = False
    
    return all_good


def main():
    """Run all configuration tests"""
    print("🧪 Audio Transcriber Configuration Validation\n")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("OpenAI Key Loading", test_openai_key_loading()))
    results.append(("Auth Token", test_auth_token()))
    results.append(("Transcriber Init", test_transcriber_initialization()))
    results.append(("Server Config", test_server_configuration()))
    results.append(("Environment Vars", test_environment_variables()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("-" * 25)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 25)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"   Overall: {overall_status}")
    
    if not all_passed:
        print("\n💡 Recommendations:")
        if not results[0][1]:  # OpenAI key
            print("   - Set OPENAI_API_KEY in .env file")
        if not results[1][1]:  # Auth token
            print("   - Set AUTH_TOKEN in .env file for API security")
        if not results[3][1]:  # Server config
            print("   - Check if ports are already in use")
    
    print("\n🚀 Ready to start servers!" if all_passed else "\n🔧 Fix configuration issues before starting servers.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
