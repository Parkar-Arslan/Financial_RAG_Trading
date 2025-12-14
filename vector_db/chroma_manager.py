import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import uuid
from tqdm import tqdm
from config.settings import Settings

class ChromaDBManager:
    """Manager for ChromaDB vector database (FREE)"""
    
    def __init__(self):
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=Settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = Settings.CHROMA_COLLECTION_NAME
        self.setup_collection()
    
    def setup_collection(self):
        """Setup ChromaDB collection"""
        try:
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Financial documents for RAG"}
            )
            
            print(f"Collection '{self.collection_name}' ready")
            print(f"Current document count: {self.collection.count()}")
            
        except Exception as e:
            print(f"Error setting up ChromaDB collection: {e}")
            raise
    
    def add_documents(self, 
                     documents: List[Dict], 
                     embeddings: List[List[float]],
                     batch_size: int = 100) -> Dict:
        """Add documents with embeddings to ChromaDB"""
        
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        successful = 0
        failed = 0
        
        # Process in batches
        for i in tqdm(range(0, len(documents), batch_size), desc="Adding to ChromaDB"):
            batch_docs = documents[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size]
            
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            embeddings_list = []
            
            for j, doc in enumerate(batch_docs):
                # Generate unique ID
                doc_id = str(uuid.uuid4())
                
                # Extract text and metadata
                text = doc.get('text', '')
                
                # Prepare metadata (ChromaDB requires all values to be strings, ints, floats, or bools)
                # We ensure all values are simple types to avoid ChromaDB errors
                metadata = {
                    'ticker': str(doc.get('ticker', 'UNKNOWN')),
                    'company_name': str(doc.get('company_name', '')),
                    'document_type': str(doc.get('type', '')),
                    'date': str(doc.get('date', '')),
                    'chunk_id': str(doc.get('chunk_id', 0)),
                    'sector': str(doc.get('metadata', {}).get('sector', '')),
                    'industry': str(doc.get('metadata', {}).get('industry', '')),
                    # Convert stats to string to ensure compatibility
                    'market_cap': str(doc.get('metadata', {}).get('market_cap', 0)),
                    'pe_ratio': str(doc.get('metadata', {}).get('pe_ratio', 0))
                }
                
                ids.append(doc_id)
                texts.append(text)
                metadatas.append(metadata)
                embeddings_list.append(batch_embeddings[j])
            
            try:
                # Add to collection
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings_list
                )
                successful += len(batch_docs)
                
            except Exception as e:
                print(f"Error in batch {i//batch_size}: {e}")
                failed += len(batch_docs)
        
        print(f"Added {successful} documents to ChromaDB")
        
        return {
            'successful': successful,
            'failed': failed,
            'total': len(documents)
        }
    
    def search(self, 
              query_embedding: List[float], 
              filters: Dict = None,
              top_k: int = 5) -> List[Dict]:
        """Search for similar documents in ChromaDB"""
        
        try:
            # Build where clause with explicit $and operator for ChromaDB
            where_clause = None
            
            if filters:
                conditions = []
                
                if 'tickers' in filters and filters['tickers']:
                    conditions.append({'ticker': {"$in": filters['tickers']}})
                
                if 'doc_types' in filters and filters['doc_types']:
                    conditions.append({'document_type': {"$in": filters['doc_types']}})
                
                # CRITICAL FIX: Use $and if multiple conditions exist
                if len(conditions) > 1:
                    where_clause = {"$and": conditions}
                elif len(conditions) == 1:
                    where_clause = conditions[0]
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # ... (rest of the function remains the same) ...
            
            # Format results
            formatted_results = []
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        # Handle case where distances might be None
                        'score': 1 - results['distances'][0][i] if results['distances'] else 0,
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name,
                'persist_directory': Settings.CHROMA_PERSIST_DIR
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def reset_collection(self):
        """Reset the collection (delete all documents)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.setup_collection()
            print(f"Collection '{self.collection_name}' reset successfully")
        except Exception as e:
            print(f"Error resetting collection: {e}")