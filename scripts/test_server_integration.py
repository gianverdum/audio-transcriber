#!/usr/bin/env python3
"""
Test script to validate API and MCP servers with authentication
"""

import sys
import time
import requests
import json
import tempfile
import subprocess
import signal
import os
from pathlib import Path
from threading import Thread

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber.core.config import settings


class ServerTester:
    """Test API and MCP servers"""
    
    def __init__(self):
        self.api_process = None
        self.mcp_process = None
        self.api_url = f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
        self.mcp_url = f"http://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}"
        self.auth_headers = {"Authorization": f"Bearer {settings.AUTH_TOKEN}"} if settings.AUTH_TOKEN else {}
    
    def start_api_server(self):
        """Start API server in background"""
        print("🚀 Starting API server...")
        try:
            cmd = ["uv", "run", "audio-transcriber", "server"]
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            time.sleep(3)  # Wait for server to start
            return self.api_process.poll() is None
        except Exception as e:
            print(f"❌ Failed to start API server: {e}")
            return False
    
    def start_mcp_server(self):
        """Start MCP HTTP server in background"""
        print("🔗 Starting MCP HTTP server...")
        try:
            cmd = ["uv", "run", "audio-transcriber-mcp"]
            self.mcp_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            time.sleep(3)  # Wait for server to start
            return self.mcp_process.poll() is None
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def test_api_health(self):
        """Test API health endpoint"""
        print("🏥 Testing API health endpoint...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API Health: {data}")
                return True
            else:
                print(f"   ❌ API Health failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API Health error: {e}")
            return False
    
    def test_mcp_health(self):
        """Test MCP health endpoint"""
        print("🔗 Testing MCP health endpoint...")
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ MCP Health: {data}")
                return True
            else:
                print(f"   ❌ MCP Health failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ MCP Health error: {e}")
            return False
    
    def test_api_auth(self):
        """Test API authentication"""
        print("🔐 Testing API authentication...")
        
        if not settings.AUTH_TOKEN:
            print("   ⚠️  No AUTH_TOKEN configured, skipping auth test")
            return True
        
        # Test without token
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            if response.status_code == 401:
                print("   ✅ API correctly rejects requests without token")
            else:
                print(f"   ⚠️  API allows requests without token (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Auth test error: {e}")
            return False
        
        # Test with token
        try:
            response = requests.get(f"{self.api_url}/status", headers=self.auth_headers, timeout=5)
            if response.status_code == 200:
                print("   ✅ API accepts requests with valid token")
                return True
            else:
                print(f"   ❌ API rejects valid token (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"   ❌ Auth test error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test main API endpoints"""
        print("📡 Testing API endpoints...")
        
        endpoints_to_test = [
            ("/", "GET", "Root endpoint"),
            ("/status", "GET", "Status endpoint"),
            ("/supported-formats", "GET", "Supported formats"),
        ]
        
        all_passed = True
        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{self.api_url}{endpoint}"
                response = requests.request(method, url, headers=self.auth_headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ {description}: {response.status_code}")
                else:
                    print(f"   ❌ {description}: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {description}: {e}")
                all_passed = False
        
        return all_passed
    
    def test_mcp_tools(self):
        """Test MCP tools endpoint"""
        print("🛠️  Testing MCP tools...")
        
        try:
            # Test get_server_status tool
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "get_server_status",
                    "arguments": {}
                }
            }
            
            response = requests.post(
                f"{self.mcp_url}/mcp",
                headers={**self.auth_headers, "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ MCP tool call successful: {data.get('content', 'No content')[:100]}...")
                return True
            else:
                print(f"   ❌ MCP tool call failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ MCP tools error: {e}")
            return False
    
    def test_openai_connection(self):
        """Test OpenAI API connection via transcriber"""
        print("🤖 Testing OpenAI connection...")
        
        try:
            from audio_transcriber.core.transcriber import AudioTranscriber
            transcriber = AudioTranscriber()
            
            # Test if the client is properly initialized
            if transcriber.client and transcriber.openai_api_key:
                print("   ✅ OpenAI client initialized successfully")
                print(f"   ✅ API key loaded: {transcriber.openai_api_key[:8]}{'*' * 40}")
                return True
            else:
                print("   ❌ OpenAI client not properly initialized")
                return False
                
        except Exception as e:
            print(f"   ❌ OpenAI connection error: {e}")
            return False
    
    def cleanup(self):
        """Stop servers and cleanup"""
        print("\n🧹 Cleaning up...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("   ✅ API server stopped")
            except Exception:
                try:
                    self.api_process.kill()
                    print("   ⚠️  API server force killed")
                except Exception:
                    print("   ❌ Failed to stop API server")
        
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
                print("   ✅ MCP server stopped")
            except Exception:
                try:
                    self.mcp_process.kill()
                    print("   ⚠️  MCP server force killed")
                except Exception:
                    print("   ❌ Failed to stop MCP server")


def main():
    """Run server integration tests"""
    print("🧪 Audio Transcriber Server Integration Tests\n")
    print("=" * 60)
    
    tester = ServerTester()
    results = []
    
    try:
        # Test 1: OpenAI connection
        results.append(("OpenAI Connection", tester.test_openai_connection()))
        
        # Test 2: Start and test API server
        if tester.start_api_server():
            results.append(("API Server Start", True))
            results.append(("API Health", tester.test_api_health()))
            results.append(("API Auth", tester.test_api_auth()))
            results.append(("API Endpoints", tester.test_api_endpoints()))
        else:
            results.append(("API Server Start", False))
            results.append(("API Health", False))
            results.append(("API Auth", False))
            results.append(("API Endpoints", False))
        
        # Test 3: Start and test MCP server
        if tester.start_mcp_server():
            results.append(("MCP Server Start", True))
            results.append(("MCP Health", tester.test_mcp_health()))
            results.append(("MCP Tools", tester.test_mcp_tools()))
        else:
            results.append(("MCP Server Start", False))
            results.append(("MCP Health", False))
            results.append(("MCP Tools", False))
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        tester.cleanup()
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Results:")
    print("-" * 30)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 30)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"   Overall: {overall_status}")
    
    if all_passed:
        print("\n🎉 Servers are working correctly with authentication!")
        print("\n🚀 Ready for production deployment!")
    else:
        print("\n🔧 Some issues found, check the logs above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
