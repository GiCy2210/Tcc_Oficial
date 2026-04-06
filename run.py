#!/usr/bin/env python3
"""
Ponto de entrada principal do sistema.
Execute este arquivo para iniciar a aplicação.
"""

import subprocess
import sys
import os

def main():
    print("🚀 Iniciando o Sistema de Correção de Redações ENEM...")
    
    # Verifica se o arquivo .env existe
    if not os.path.exists(".env"):
        print("⚠️  Arquivo .env não encontrado!")
        print("📝 Crie um arquivo .env com: GEMINI_API_KEY=sua_chave_aqui")
        sys.exit(1)
    
    # Adiciona o diretório atual ao PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # Executa o Streamlit
    try:
        subprocess.run(
            ["streamlit", "run", "app/main.py"],
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado.")
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

if __name__ == "__main__":
    main()