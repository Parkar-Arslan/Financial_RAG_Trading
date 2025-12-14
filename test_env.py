import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print("\nInstalled packages:")

packages = ['groq', 'streamlit', 'chromadb', 'sentence_transformers', 'yfinance']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg} is installed")
    except ImportError:
        print(f"❌ {pkg} is NOT installed")