"""
Robust Data Loading Script
- Prioritizes loading local 'all_stocks_data.json' if it exists.
- Bypasses Yahoo Finance API errors (429) by using local data.
"""

import sys
import os
import json
import argparse
import time
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from data_collection.yahoo_collector import YahooFinanceCollector
from data_collection.data_preprocessor import DocumentPreprocessor
from vector_db.chroma_manager import ChromaDBManager
from vector_db.embeddings import LocalEmbeddings

def main():
    print("="*60)
    print("🚀 Financial RAG Data Loading Script (Local Priority)")
    print("="*60)
    
    # Initialize components
    chroma_manager = ChromaDBManager()
    preprocessor = DocumentPreprocessor()
    embedder = LocalEmbeddings()
    collector = YahooFinanceCollector()

    # Step 1: Get Data (Local Priority)
    print("\n📊 Step 1: Acquiring financial data...")
    stocks_data = []
    
    local_file = os.path.join("data", "raw", "all_stocks_data.json")
    
    # OPTION A: Load from existing local file (Bypasses API)
    if os.path.exists(local_file):
        print(f"   📂 Found local file: {local_file}")
        try:
            with open(local_file, 'r') as f:
                stocks_data = json.load(f)
            print(f"   ✅ Loaded {len(stocks_data)} stocks from local file.")
        except Exception as e:
            print(f"   ❌ Error reading local file: {e}")
    
    # OPTION B: Fetch from API (Only if local file missing)
    if not stocks_data:
        print("   ⚠️ Local file not found or empty. Fetching from Yahoo Finance...")
        tickers = Settings.DEFAULT_TICKERS
        stocks_data = collector.collect_multiple_tickers(tickers)

    if not stocks_data:
        print("❌ No data available to process. Exiting.")
        return

    # Step 2: Process Documents
    print("\n📝 Step 2: Processing and Chunking...")
    processed_chunks = preprocessor.process_all_stocks(stocks_data)
    print(f"   ✅ Created {len(processed_chunks)} document chunks")

    # Step 3: Embed and Store
    print("\n🧠 Step 3: Generating Embeddings & Storing...")
    
    # Clear old data to prevent duplicates/conflicts
    chroma_manager.reset_collection()
    
    # Batch process to be safe
    batch_size = 32
    total_added = 0
    
    for i in tqdm(range(0, len(processed_chunks), batch_size), desc="Embedding"):
        batch = processed_chunks[i : i + batch_size]
        texts = [chunk['text'] for chunk in batch]
        
        try:
            embeddings = embedder.generate_embeddings_batch(texts)
            result = chroma_manager.add_documents(batch, embeddings)
            total_added += result.get('successful', 0)
        except Exception as e:
            print(f"   ❌ Error in batch {i}: {e}")

    print("\n" + "="*60)
    print("🎉 Success! Database is ready.")
    print(f"   Total Documents: {total_added}")
    print("="*60)

if __name__ == "__main__":
    main()