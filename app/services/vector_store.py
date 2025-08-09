from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            raise
            
        self.embeddings = None
        self.texts = []
        self.metadata = []

    def add_documents(self, texts: List[str], metadata: List[dict] = None):
        """Add documents to vector store"""
        if not texts:
            return
            
        try:
            # Generate embeddings
            new_embeddings = self.model.encode(texts, show_progress_bar=False)
            
            # Store embeddings
            if self.embeddings is None:
                self.embeddings = new_embeddings
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
            # Store texts and metadata
            self.texts.extend(texts)
            if metadata:
                self.metadata.extend(metadata)
            else:
                self.metadata.extend([{}] * len(texts))
                
            logger.info(f"Added {len(texts)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float, dict]]:
        """Search for similar documents using cosine similarity"""
        if self.embeddings is None or len(self.texts) == 0:
            logger.warning("Vector store is empty, returning no results")
            return []
            
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query], show_progress_bar=False)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                if idx < len(self.texts):
                    score = float(similarities[idx])
                    results.append((
                        self.texts[idx],
                        score,
                        self.metadata[idx] if idx < len(self.metadata) else {}
                    ))
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []