#!/usr/bin/env python3
"""
Script to test the Audio Transcriber MCP Server
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def test_mcp_server_startup():
    """Test if the MCP server starts correctly"""
    print("🧪 Testing MCP Server initialization...")
    
    try:
        # Try to import MCP dependencies
        from audio_transcriber.mcp.server import main
        print("✅ MCP dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing MCP dependencies: {e}")
        print("💡 Run: uv add mcp httpx")
        return False


def test_mcp_tools_definition():
    """Test if MCP tools are defined correctly"""
    print("\n🔧 Testing MCP tools definition...")
    
    try:
        from audio_transcriber.mcp.server import list_tools
        
        # Simulate an async call
        import asyncio
        
        async def test_list_tools():
            tools = await list_tools()
            return tools
        
        tools = asyncio.run(test_list_tools())
        
        expected_tools = {
            "transcribe_audio",
            "transcribe_batch", 
            "get_server_status",
            "list_supported_formats"
        }
        
        found_tools = {tool.name for tool in tools}
        
        if expected_tools.issubset(found_tools):
            print("✅ All expected tools are defined")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            return True
        else:
            missing = expected_tools - found_tools
            print(f"❌ Missing tools: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tools: {e}")
        return False


def test_mcp_models():
    """Test if Pydantic models are working"""
    print("\n📋 Testing MCP data models...")
    
    try:
        from audio_transcriber.mcp.models import (
            TranscribeAudioInput,
            TranscribeAudioOutput,
            BatchTranscribeInput,
            ServerStatusOutput
        )
        
        # Test TranscribeAudioInput
        input_data = TranscribeAudioInput(
            audio_url="https://example.com/test.mp3",
            language="pt",
            max_file_size_mb=10
        )
        print("✅ TranscribeAudioInput validated successfully")
        
        # Test BatchTranscribeInput
        batch_input = BatchTranscribeInput(
            audio_urls=["https://example.com/test1.mp3", "https://example.com/test2.wav"],
            language="en"
        )
        print("✅ BatchTranscribeInput validated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False


def test_mcp_service():
    """Test if the MCP service is working"""
    print("\n⚙️ Testing MCP service...")
    
    try:
        from audio_transcriber.mcp.service import MCPTranscriptionService
        
        service = MCPTranscriptionService()
        print("✅ MCP service created successfully")
        
        # Test server status
        import asyncio
        
        async def test_status():
            status = await service.get_server_status()
            return status
        
        status = asyncio.run(test_status())
        print(f"✅ Server status: {status.status}")
        print(f"   OpenAI available: {status.openai_api_available}")
        print(f"   Supported formats: {len(status.supported_formats)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing service: {e}")
        return False


def test_openai_configuration():
    """Test if OpenAI configuration is correct"""
    print("\n🔑 Testing OpenAI configuration...")
    
    try:
        from audio_transcriber.core.config import settings
        
        if settings.validate_openai_key():
            print("✅ OpenAI key configured correctly")
            return True
        else:
            print("❌ OpenAI key not configured")
            print("💡 Set OPENAI_API_KEY in .env file")
            return False
            
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False


def create_example_mcp_config():
    """Create an example MCP configuration file"""
    print("\n📄 Creating example MCP configuration...")
    
    config = {
        "mcpServers": {
            "audio-transcriber": {
                "command": "uv",
                "args": ["run", "audio-transcriber-mcp"],
                "cwd": str(Path.cwd()),
                "env": {
                    "OPENAI_API_KEY": "your-openai-api-key-here"
                }
            }
        }
    }
    
    config_file = Path("mcp-config-example.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration created: {config_file}")
    print("💡 To use with Claude Desktop, copy this content to:")
    print("   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   - Windows: %APPDATA%\\Claude\\claude_desktop_config.json")


def main():
    """Main test function"""
    print("🎵 Audio Transcriber - MCP Server Test")
    print("=" * 50)
    
    tests = [
        test_openai_configuration,
        test_mcp_server_startup,
        test_mcp_models,
        test_mcp_tools_definition,
        test_mcp_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP Server is ready for use.")
        create_example_mcp_config()
        
        print("\n🚀 To start the MCP Server:")
        print("   uv run audio-transcriber-mcp")
        
    else:
        print("⚠️  Some tests failed. Check dependencies and configuration.")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
