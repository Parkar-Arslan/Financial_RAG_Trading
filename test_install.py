print("Testing installations...")

try:
    import chromadb
    print("✅ ChromaDB installed")
except ImportError as e:
    print(f"❌ ChromaDB not installed: {e}")

try:
    import sentence_transformers
    print("✅ Sentence Transformers installed")
except ImportError as e:
    print(f"❌ Sentence Transformers not installed: {e}")

try:
    import yfinance
    print("✅ yfinance installed")
except ImportError as e:
    print(f"❌ yfinance not installed: {e}")

try:
    import groq
    print("✅ Groq installed")
except ImportError as e:
    print(f"❌ Groq not installed: {e}")

try:
    import streamlit
    print("✅ Streamlit installed")
except ImportError as e:
    print(f"❌ Streamlit not installed: {e}")

print("\nAll tests complete!")