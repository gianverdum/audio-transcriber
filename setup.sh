#!/bin/bash

# Script de instalação para Audio Transcriber
# Execute: chmod +x setup.sh && ./setup.sh

echo "🚀 Configurando Audio Transcriber..."
echo "=================================="

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale o Python 3 primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Instale o pip primeiro."
    exit 1
fi

echo "✅ pip encontrado"

# Cria ambiente virtual (opcional)
read -p "🤔 Deseja criar um ambiente virtual? (s/N): " create_venv
if [[ $create_venv =~ ^[Ss]$ ]]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
    echo "💡 Para ativar novamente: source venv/bin/activate"
fi

# Instala dependências
echo "📥 Instalando dependências..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Cria pastas necessárias
echo "📁 Criando estrutura de pastas..."
mkdir -p audios output
echo "✅ Pastas criadas: audios/ e output/"

# Solicita chave da OpenAI
echo ""
echo "🔑 Configuração da OpenAI"
echo "========================"
echo "Você precisa de uma chave da API OpenAI."
echo "Obtenha em: https://platform.openai.com/account/api-keys"
echo ""

read -p "Digite sua chave da OpenAI (ou pressione Enter para configurar depois): " openai_key

if [ ! -z "$openai_key" ]; then
    # Adiciona ao bashrc/zshrc
    if [ -f ~/.bashrc ]; then
        echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bashrc
        echo "✅ Chave adicionada ao ~/.bashrc"
    fi
    
    if [ -f ~/.zshrc ]; then
        echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.zshrc
        echo "✅ Chave adicionada ao ~/.zshrc"
    fi
    
    # Define para a sessão atual
    export OPENAI_API_KEY="$openai_key"
    echo "✅ Chave configurada para a sessão atual"
else
    echo "⚠️  Configure a chave depois:"
    echo "   export OPENAI_API_KEY=\"sua_chave_aqui\""
fi

# Executa teste de configuração
echo ""
echo "🧪 Executando teste de configuração..."
python3 test_setup.py

echo ""
echo "🎉 Instalação concluída!"
echo "======================="
echo ""
echo "📖 Próximos passos:"
echo "1. Coloque seus arquivos de áudio na pasta 'audios/'"
echo "2. Execute: python3 exemplo_uso.py"
echo "3. Ou use: python3 audio_transcriber.py audios/"
echo ""
echo "📚 Veja o README.md para mais informações"

# Se criou ambiente virtual, lembra de ativá-lo
if [[ $create_venv =~ ^[Ss]$ ]]; then
    echo ""
    echo "💡 Lembre-se de ativar o ambiente virtual:"
    echo "   source venv/bin/activate"
fi
