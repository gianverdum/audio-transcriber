#!/usr/bin/env python3
"""
Utility script for initial Audio Transcriber setup
Helps create and configure the .env file
"""

import os
import sys
from pathlib import Path
import shutil

def create_env_file():
    """Creates .env file based on .env.example"""
    
    projeto_dir = Path(__file__).parent.parent
    env_example = projeto_dir / ".env.example"
    env_file = projeto_dir / ".env"
    
    print("🔧 Audio Transcriber Setup")
    print("=" * 40)
    
    # Check if .env.example exists
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite not in ['s', 'sim', 'y', 'yes']:
            print("⏹️  Operation cancelled")
            return False
    
    # Copy .env.example to .env
    try:
        shutil.copy2(env_example, env_file)
        print(f"✅ .env file created at: {env_file}")
    except Exception as e:
        print(f"❌ Error creating .env: {e}")
        return False
    
    return True

def configure_openai_key():
    """Helps configure the OpenAI key"""
    
    projeto_dir = Path(__file__).parent.parent
    env_file = projeto_dir / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found. Run creation first.")
        return False
    
    print("\n🔑 OpenAI Key Setup")
    print("=" * 40)
    print("🌐 Get your key at: https://platform.openai.com/account/api-keys")
    print()
    
    # Request the key
    key = input("Paste your OpenAI key here: ").strip()
    
    if not key:
        print("⚠️  No key provided")
        return False
    
    # Basic format validation
    if not key.startswith('sk-'):
        print("⚠️  OpenAI keys usually start with 'sk-'")
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed not in ['s', 'sim', 'y', 'yes']:
            return False
    
    # Read current .env file
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False
    
    # Update the key line
    for i, line in enumerate(lines):
        if line.startswith('OPENAI_API_KEY='):
            lines[i] = f'OPENAI_API_KEY={key}\n'
            break
    
    # Save updated file
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("✅ OpenAI key configured successfully!")
        return True
    except Exception as e:
        print(f"❌ Error saving .env: {e}")
        return False

def check_configuration():
    """Checks if the configuration is correct"""
    
    print("\n🧪 Checking Configuration")
    print("=" * 40)
    
    projeto_dir = Path(__file__).parent.parent
    env_file = projeto_dir / ".env"
    
    # Check if .env exists
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file found")
    
    # Load and check the key
    try:
        from dotenv import load_dotenv # type: ignore[import]
        load_dotenv(env_file)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in .env")
            return False
        
        if api_key == 'sk-proj-your_openai_key_here':
            print("❌ OpenAI key not configured (still example value)")
            return False
        
        print("✅ OpenAI key configured")
        print(f"   Key: {api_key[:20]}...{api_key[-8:] if len(api_key) > 28 else api_key}")
        
        return True
        
    except ImportError:
        print("⚠️  python-dotenv not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False

def main():
    """Main function for setup script"""
    
    print("🚀 Audio Transcriber - Initial Setup")
    print("=" * 50)
    
    # Options menu
    while True:
        print("\nOptions:")
        print("1. Create .env file")
        print("2. Configure OpenAI key")
        print("3. Check configuration")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == '1':
            create_env_file()
        elif choice == '2':
            configure_openai_key()
        elif choice == '3':
            if check_configuration():
                print("\n🎉 Setup complete! You can use Audio Transcriber.")
            else:
                print("\n⚠️  Incomplete setup. Complete the steps above.")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
