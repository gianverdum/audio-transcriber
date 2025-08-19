#!/usr/bin/env python3
"""
Advanced usage example of the transcription tool
Demonstrates programmatic use with custom configurations
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

 # Load environment variables from .env file
load_dotenv()

 # Add the src directory to the path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_transcriber import AudioTranscriber

def setup_logging():
    """Setup custom logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'transcricao_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

def advanced_example():
    """Example with more advanced usage of the tool"""
    
    print("🎵 Audio Transcriber - Advanced Example")
    print("=" * 45)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Configurations (now come from the .env file)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  Please configure OPENAI_API_KEY in the .env file before continuing")
            print("💡 Copy .env.example to .env and set your credentials")
            return
        
        # Create the transcriber with custom configurations
        transcriber = AudioTranscriber(
            # Optional configurations can override those in .env
            max_file_size_mb=30,  # Example: larger file than default
            api_delay=1.0,        # Example: longer pause between requests
            save_logs=True        # Save logs to file
        )
        
        # Set folders
        audio_folder = "./audios"
        output_folder = "./output"
        
        # Create folders if they don't exist
        Path(audio_folder).mkdir(exist_ok=True)
        Path(output_folder).mkdir(exist_ok=True)
        
        # Check for files
        audio_files = transcriber.find_audio_files(audio_folder)
        if not audio_files:
            print(f"❌ No audio files found in {audio_folder}")
            print("Put some audio files in the folder and try again.")
            return
        
        print(f"📁 Found {len(audio_files)} audio files")
        
        # List found files
        print("\n📋 Files to be processed:")
        for i, file_path in enumerate(audio_files, 1):
            file_info = transcriber.get_file_info(file_path)
            print(f"  {i:2d}. {file_info['file_name']} ({file_info['size_mb']} MB)")
        
        # Confirm processing
        answer = input("\n🤔 Continue with transcription? (y/N): ").strip().lower()
        if answer not in ['y', 'yes', 's', 'sim']:
            print("⏹️  Processing cancelled")
            return
        
        # Output file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(output_folder) / f"advanced_transcriptions_{timestamp}.xlsx"
        
        # Process with timing
        start = datetime.now()
        print(f"\n🚀 Starting processing at {start.strftime('%H:%M:%S')}")
        
        excel_file = transcriber.process_folder(audio_folder, str(output_file))
        
        end = datetime.now()
        duration = end - start
        
        # Final report
        print(f"\n🎉 Processing complete!")
        print(f"⏱️  Total time: {duration}")
        print(f"📊 Excel spreadsheet: {excel_file}")
        
        # Results statistics
        if transcriber.results:
            successes = len([r for r in transcriber.results if r.get('success', '').lower() in ['yes', 'sim']])
            failures = len(transcriber.results) - successes
            success_rate = (successes / len(transcriber.results)) * 100
            
            print(f"\n📈 Statistics:")
            print(f"   Successes: {successes}")
            print(f"   Failures: {failures}")
            print(f"   Success rate: {success_rate:.1f}%")
            
            if failures > 0:
                print(f"\n❌ Failed files:")
                for result in transcriber.results:
                    if result.get('success', '').lower() in ['no', 'não']:
                        print(f"   - {result.get('file_name', 'unknown')}: {result.get('error', 'unknown error')}")
        
        logger.info("Advanced processing completed successfully")
        
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
    except Exception as e:
        logger.error(f"Error in advanced example: {e}")
        print(f"❌ Error: {e}")

def batch_processing_example():
    """Example of processing multiple folders"""
    
    print("\n🗂️  Example: Batch Processing")
    print("=" * 40)
    
    audio_folders = [
        "./audios/meeting1",
        "./audios/meeting2", 
        "./audios/interviews"
    ]
    
    try:
        transcriber = AudioTranscriber()
        
        for folder in audio_folders:
            if Path(folder).exists():
                print(f"\n📁 Processing: {folder}")
                
                folder_name = Path(folder).name
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"transcriptions_{folder_name}_{timestamp}.xlsx"
                
                excel_file = transcriber.process_folder(folder, output_file)
                print(f"✅ Done: {excel_file}")
            else:
                print(f"⚠️  Folder not found: {folder}")
                
    except Exception as e:
        print(f"❌ Error in batch processing: {e}")

if __name__ == "__main__":
    advanced_example()
    
    # Ask if want to run batch example
    answer = input("\n🤔 Run batch processing example? (y/N): ").strip().lower()
    if answer in ['y', 'yes', 's', 'sim']:
        batch_processing_example()
