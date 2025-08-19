#!/bin/bash

# Installation script for Audio Transcriber
# Run: chmod +x setup.sh && ./setup.sh

echo "🚀 Setting up Audio Transcriber..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

echo "✅ pip found"

# Create virtual environment (optional)
read -p "🤔 Do you want to create a virtual environment? (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment activated"
    echo "💡 To activate again: source venv/bin/activate"
fi

# Install dependencies
echo "📥 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

# Create required folders
echo "📁 Creating folder structure..."
mkdir -p audios output
echo "✅ Folders created: audios/ and output/"

# Request OpenAI key
echo ""
echo "🔑 OpenAI Configuration"
echo "========================"
echo "You need an OpenAI API key."
echo "Get it at: https://platform.openai.com/account/api-keys"
echo ""

read -p "Enter your OpenAI key (or press Enter to configure later): " openai_key

if [ ! -z "$openai_key" ]; then
    # Add to bashrc/zshrc
    if [ -f ~/.bashrc ]; then
        echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bashrc
        echo "✅ Key added to ~/.bashrc"
    fi
    
    if [ -f ~/.zshrc ]; then
        echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.zshrc
        echo "✅ Key added to ~/.zshrc"
    fi
    
    # Set for current session
    export OPENAI_API_KEY="$openai_key"
    echo "✅ Key configured for current session"
else
    echo "⚠️  Configure the key later:"
    echo "   export OPENAI_API_KEY=\"your_key_here\""
fi

# Run configuration test
echo ""
echo "🧪 Running configuration test..."
python3 test_setup.py

echo ""
echo "🎉 Installation complete!"
echo "======================="
echo ""
echo "📖 Next steps:"
echo "1. Place your audio files in the 'audios/' folder"
echo "2. Run: python3 example_usage.py"
echo "3. Or use: python3 audio_transcriber.py audios/"
echo ""
echo "📚 See README.md for more information"

# If virtual environment was created, remind to activate
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo ""
    echo "💡 Remember to activate the virtual environment:"
    echo "   source venv/bin/activate"
fi
