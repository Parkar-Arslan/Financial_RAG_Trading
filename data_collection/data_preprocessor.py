import re
import json
from typing import List, Dict
from datetime import datetime
import os
from tqdm import tqdm

class DocumentPreprocessor:
    """Preprocess documents for vector storage"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\%\$\/]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if len(chunk.split()) > 20:  # Minimum chunk size
                chunks.append(chunk)
        
        return chunks
    
    def process_stock_data(self, stock_data: Dict) -> List[Dict]:
        """Process stock data into chunks for vector database"""
        processed_chunks = []
        
        ticker = stock_data['ticker']
        company_name = stock_data['company_name']
        
        # Process each document
        for doc in stock_data.get('documents', []):
            # Clean content
            cleaned_content = self.clean_text(doc['content'])
            
            # Create chunks
            chunks = self.chunk_text(cleaned_content)
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    'text': chunk,
                    'ticker': ticker,
                    'company_name': company_name,
                    'type': doc['type'],
                    'chunk_id': i,
                    'date': doc['date'],
                    'metadata': {
                        'sector': stock_data.get('sector', ''),
                        'industry': stock_data.get('industry', ''),
                        'market_cap': stock_data.get('market_cap', 0),
                        'pe_ratio': stock_data.get('pe_ratio', 0)
                    }
                })
        
        return processed_chunks
    
    def process_all_stocks(self, stocks_data: List[Dict]) -> List[Dict]:
        """Process all stock data"""
        all_processed = []
        
        for stock_data in tqdm(stocks_data, desc="Processing documents"):
            chunks = self.process_stock_data(stock_data)
            all_processed.extend(chunks)
        
        print(f"Total processed chunks: {len(all_processed)}")
        
        # Save processed data
        os.makedirs("data/processed", exist_ok=True)
        output_file = "data/processed/all_chunks.json"
        with open(output_file, 'w') as f:
            json.dump(all_processed, f, indent=2, default=str)
        
        return all_processed