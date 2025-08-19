#!/usr/bin/env python3
"""
Script utilitário para configuração inicial do Audio Transcriber
Ajuda a criar e configurar o arquivo .env
"""

import os
import sys
from pathlib import Path
import shutil

def criar_arquivo_env():
    """Cria arquivo .env baseado no .env.example"""
    
    projeto_dir = Path(__file__).parent.parent
    env_example = projeto_dir / ".env.example"
    env_file = projeto_dir / ".env"
    
    print("🔧 Configuração do Audio Transcriber")
    print("=" * 40)
    
    # Verifica se .env.example existe
    if not env_example.exists():
        print("❌ Arquivo .env.example não encontrado")
        return False
    
    # Verifica se .env já existe
    if env_file.exists():
        print("⚠️  Arquivo .env já existe")
        sobrescrever = input("Deseja sobrescrever? (s/N): ").strip().lower()
        if sobrescrever not in ['s', 'sim', 'y', 'yes']:
            print("⏹️  Operação cancelada")
            return False
    
    # Copia .env.example para .env
    try:
        shutil.copy2(env_example, env_file)
        print(f"✅ Arquivo .env criado em: {env_file}")
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False
    
    return True

def configurar_chave_openai():
    """Ajuda a configurar a chave da OpenAI"""
    
    projeto_dir = Path(__file__).parent.parent
    env_file = projeto_dir / ".env"
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado. Execute a criação primeiro.")
        return False
    
    print("\n🔑 Configuração da Chave OpenAI")
    print("=" * 40)
    print("🌐 Obtenha sua chave em: https://platform.openai.com/account/api-keys")
    print()
    
    # Solicita a chave
    chave = input("Cole sua chave da OpenAI aqui: ").strip()
    
    if not chave:
        print("⚠️  Nenhuma chave fornecida")
        return False
    
    # Valida formato básico
    if not chave.startswith('sk-'):
        print("⚠️  A chave da OpenAI geralmente começa com 'sk-'")
        continuar = input("Continuar mesmo assim? (s/N): ").strip().lower()
        if continuar not in ['s', 'sim', 'y', 'yes']:
            return False
    
    # Lê o arquivo .env atual
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except Exception as e:
        print(f"❌ Erro ao ler .env: {e}")
        return False
    
    # Atualiza a linha da chave
    for i, linha in enumerate(linhas):
        if linha.startswith('OPENAI_API_KEY='):
            linhas[i] = f'OPENAI_API_KEY={chave}\n'
            break
    
    # Salva o arquivo atualizado
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(linhas)
        print("✅ Chave da OpenAI configurada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar .env: {e}")
        return False

def verificar_configuracao():
    """Verifica se a configuração está correta"""
    
    print("\n🧪 Verificando Configuração")
    print("=" * 40)
    
    projeto_dir = Path(__file__).parent.parent
    env_file = projeto_dir / ".env"
    
    # Verifica se .env existe
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    print("✅ Arquivo .env encontrado")
    
    # Carrega e verifica a chave
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada no .env")
            return False
        
        if api_key == 'sk-proj-sua_chave_openai_aqui':
            print("❌ Chave da OpenAI não foi configurada (ainda está o valor exemplo)")
            return False
        
        print("✅ Chave da OpenAI configurada")
        print(f"   Chave: {api_key[:20]}...{api_key[-8:] if len(api_key) > 28 else api_key}")
        
        return True
        
    except ImportError:
        print("⚠️  python-dotenv não instalado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def main():
    """Função principal do script de configuração"""
    
    print("🚀 Audio Transcriber - Configuração Inicial")
    print("=" * 50)
    
    # Menu de opções
    while True:
        print("\nOpções:")
        print("1. Criar arquivo .env")
        print("2. Configurar chave OpenAI")
        print("3. Verificar configuração")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == '1':
            criar_arquivo_env()
        elif opcao == '2':
            configurar_chave_openai()
        elif opcao == '3':
            if verificar_configuracao():
                print("\n🎉 Configuração completa! Você pode usar o Audio Transcriber.")
            else:
                print("\n⚠️  Configuração incompleta. Complete os passos acima.")
        elif opcao == '4':
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
