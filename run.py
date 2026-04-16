"""
CorretorIA ENEM — Ponto de entrada.
Execute: python run.py
"""
import subprocess, sys, os
from pathlib import Path
def main():
    print("\n" + "="*52)
    print("  CorretorIA ENEM  —  v3.0")
    print("="*52)
    try:
        import flask, google.generativeai
    except ImportError:
        print("\n📦 Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    Path("data").mkdir(exist_ok=True)
    print("\n🚀 Servidor em http://localhost:5000")
    print("   Pressione Ctrl+C para parar\n")
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from app.server import app
    app.run(debug=False, port=5000, host="0.0.0.0")

if __name__ == "__main__":
    main()