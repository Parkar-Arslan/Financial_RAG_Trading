from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from tqdm import tqdm
from config.settings import Settings

class LocalEmbeddings:
    """Generate embeddings using free local models"""
    
    def __init__(self):
        # Load free sentence transformer model
        print(f"Loading embedding model: {Settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(Settings.EMBEDDING_MODEL)
        print("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i+batch_size]
            
            # Generate embeddings for batch
            batch_embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert to list and add to results
            for embedding in batch_embeddings:
                all_embeddings.append(embedding.tolist())
        
        return all_embeddings