#!/usr/bin/env python3
"""
Simple usage example of the transcription tool
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

 # Load environment variables from .env file
load_dotenv()

 # Add the src directory to the path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber import AudioTranscriber

def example_usage():
    """Basic example of how to use the tool"""
    
    print("🎵 Audio Transcriber - Usage Example")
    print("=" * 40)
    
    # Environment variables are automatically loaded from the .env file
    # You can also set them directly in the code (not recommended for production)
    # api_key = "your_key_here"
    
    try:
        # Create the transcriber (using .env file)
        transcriber = AudioTranscriber()
        
        # Option with direct key:
        # transcriber = AudioTranscriber(api_key=api_key)
        
        # Set the folder with audios
        audio_folder = input("Enter the path to the folder with audio files: ").strip()
        
        if not audio_folder:
            audio_folder = "./audios"  # default folder
        
        # Process the audios
        print(f"\n🎵 Starting transcription of audios in: {audio_folder}")
        print("⏳ Please wait, this may take a few minutes...")
        
        excel_file = transcriber.process_folder(audio_folder)
        
        print(f"\n✅ Done!")
        print(f"📊 Excel spreadsheet created: {excel_file}")
        print("\nThe spreadsheet contains:")
        print("- 'Transcriptions' sheet: all detailed transcriptions")
        print("- 'Summary' sheet: processing statistics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTips:")
        print("1. Check if the .env file is configured (copy from .env.example)")
        print("2. Confirm the OpenAI key is in the .env file")
        print("3. Confirm the audio folder exists")
        print("4. Make sure there are audio files in the folder")

if __name__ == "__main__":
    example_usage()
