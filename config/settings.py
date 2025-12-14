import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # LLM Settings - FREE Options
    USE_OLLAMA = os.getenv('USE_OLLAMA', 'False').lower() == 'true'
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # Model Settings - Updated December 2024
    if USE_OLLAMA:
        LLM_MODEL = OLLAMA_MODEL
        LLM_PROVIDER = 'ollama'
    else:
        # WORKING MODEL as of December 2024
        LLM_MODEL = 'llama-3.1-8b-instant'  # Confirmed working!
        LLM_PROVIDER = 'groq'
    
    # Embedding Model (Free, Local)
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    EMBEDDING_DIMENSION = 384
    
    # ChromaDB Settings (Free, Local)
    CHROMA_PERSIST_DIR = "./chroma_db"
    CHROMA_COLLECTION_NAME = "financial_documents"
    
    # Data Settings
    DATA_DIR = "data"
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    SAMPLE_DATA_DIR = os.path.join(DATA_DIR, "sample")
    
    # Application Settings
    APP_NAME = "Financial Research RAG Assistant (Free)"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Default tickers for analysis
    DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ"]
    
    # Document types - Fixed to match actual data
    DOCUMENT_TYPES = ["Company Overview", "Financial Performance", "Technical Analysis", "Trading Signals", "News"]
    
    # Chunk settings for document processing
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # Free model limits
    MAX_TOKENS = 1024
    TEMPERATURE = 0.7
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.USE_OLLAMA and not cls.GROQ_API_KEY:
            print("Warning: No Groq API key found. Get one free at https://console.groq.com/keys")
            print("Or set USE_OLLAMA=True to use local Ollama")
            return False
        return True