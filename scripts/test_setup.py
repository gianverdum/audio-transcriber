#!/usr/bin/env python3
"""
Script de teste para verificar a instalação e configuração
"""

import os
import sys
from pathlib import Path

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import openai
        print("✅ OpenAI instalado")
    except ImportError:
        print("❌ OpenAI não encontrado. Execute: pip install openai")
        return False
    
    try:
        import pandas
        print("✅ Pandas instalado")
    except ImportError:
        print("❌ Pandas não encontrado. Execute: pip install pandas")
        return False
    
    try:
        import openpyxl
        print("✅ OpenPyXL instalado")
    except ImportError:
        print("❌ OpenPyXL não encontrado. Execute: pip install openpyxl")
        return False
    
    return True

def verificar_chave_openai():
    """Verifica se a chave da OpenAI está configurada"""
    print("\n🔑 Verificando chave da OpenAI...")
    
    # Carrega .env primeiro
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv não instalado, tentando variável de ambiente direta")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Chave da OpenAI não encontrada")
        print("Configure no arquivo .env ou como variável de ambiente")
        print("Exemplo .env: OPENAI_API_KEY='sua_chave_aqui'")
        return False
    
    if api_key.startswith('sk-'):
        print("✅ Chave da OpenAI configurada")
        return True
    else:
        print("⚠️  Formato da chave parece incorreto (deveria começar com 'sk-')")
        return False

def verificar_estrutura_projeto():
    """Verifica se os arquivos do projeto estão presentes"""
    print("\n📁 Verificando estrutura do projeto...")
    
    arquivos_necessarios = [
        'src/audio_transcriber/__init__.py',
        'src/audio_transcriber/transcriber.py',
        'src/audio_transcriber/cli.py',
        'pyproject.toml',
        '.env.example',
        'README.md'
    ]
    
    todos_presentes = True
    for arquivo in arquivos_necessarios:
        if Path(arquivo).exists():
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} não encontrado")
            todos_presentes = False
    
    return todos_presentes

def teste_importacao():
    """Testa se o módulo principal pode ser importado"""
    print("\n📦 Testando importação do módulo...")
    
    try:
        # Adiciona src ao path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from audio_transcriber import AudioTranscriber
        print("✅ Módulo AudioTranscriber importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return False

def criar_pasta_teste():
    """Cria uma pasta de exemplo para testes"""
    print("\n📂 Criando estrutura de teste...")
    
    try:
        # Cria pastas de exemplo
        Path("./audios").mkdir(exist_ok=True)
        Path("./output").mkdir(exist_ok=True)
        
        print("✅ Pastas criadas:")
        print("  - ./audios (coloque seus arquivos de áudio aqui)")
        print("  - ./output (planilhas Excel serão salvas aqui)")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar pastas: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE CONFIGURAÇÃO - Audio Transcriber")
    print("=" * 50)
    
    # Lista de verificações
    verificacoes = [
        ("Dependências", verificar_dependencias),
        ("Chave OpenAI", verificar_chave_openai),
        ("Estrutura do projeto", verificar_estrutura_projeto),
        ("Importação do módulo", teste_importacao),
        ("Criação de pastas", criar_pasta_teste)
    ]
    
    resultados = []
    
    for nome, funcao in verificacoes:
        resultado = funcao()
        resultados.append((nome, resultado))
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{nome:.<30} {status}")
        if sucesso:
            sucessos += 1
    
    print("\n" + "=" * 50)
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("Sua instalação está pronta para uso.")
        print("\nPara começar:")
        print("1. Coloque seus áudios na pasta './audios'")
        print("2. Execute: python exemplo_uso.py")
    else:
        print(f"⚠️  {len(resultados) - sucessos} teste(s) falharam")
        print("Corrija os problemas antes de usar a ferramenta.")
    
    return 0 if sucessos == len(resultados) else 1

if __name__ == "__main__":
    exit(main())
