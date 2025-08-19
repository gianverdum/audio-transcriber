#!/usr/bin/env python3
"""
Test script to demonstrate centralized configurations
"""

from audio_transcriber.core.config import settings

print("🔧 Centralized Configurations of Audio Transcriber")
print("=" * 50)

print("\n📡 Server Configurations:")
print(f"  Host: {settings.SERVER_HOST}")
print(f"  Port: {settings.SERVER_PORT}")
print(f"  Workers: {settings.SERVER_WORKERS}")
print(f"  Reload: {settings.SERVER_RELOAD}")

print("\n🎵 API Configurations:")
print(f"  Title: {settings.API_TITLE}")
print(f"  Version: {settings.API_VERSION}")
print(f"  Description: {settings.API_DESCRIPTION[:50]}...")

print("\n⚙️ General Configurations:")
print(f"  Max File Size: {settings.MAX_FILE_SIZE_MB}MB")
print(f"  API Timeout: {settings.API_TIMEOUT}s")
print(f"  API Delay: {settings.API_DELAY}s")
print(f"  Log Level: {settings.LOG_LEVEL}")

print("\n🔗 URLs:")
print(f"  Server: {settings.get_server_url()}")
print(f"  Docs: {settings.get_server_url()}/docs")
print(f"  Health: {settings.get_server_url()}/health")

print("\n🔑 OpenAI:")
openai_configured = settings.validate_openai_key()
print(f"  Key configured: {'✅ Yes' if openai_configured else '❌ No'}")

print("\n💡 Tips:")
print("  - Set SERVER_PORT in .env to change the default port")
print("  - Use SERVER_HOST=0.0.0.0 to accept external connections")
print("  - SERVER_RELOAD=true enables auto-reload in development")
print("  - CLI arguments always override .env configurations")
