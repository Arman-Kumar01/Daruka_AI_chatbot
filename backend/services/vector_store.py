"""
Vector Store & Retrieval Service for Darukaa.Earth Knowledge Base.
Provides genuine semantic retrieval, cosine similarity ranking, source metadata extraction,
and inspectable evidence tracing.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.config import settings
from backend.models.schemas import RetrievedChunk

logger = logging.getLogger("vector_store")
logger.setLevel(logging.INFO)


class VectorStoreService:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.chroma_client = None
        self.chroma_collection = None
        self.use_chroma = False
        self.initialized = False
        self._initialize()

    def _initialize(self):
        """Loads processed knowledge chunks and builds the semantic retrieval index."""
        processed_path = settings.PROCESSED_FILE
        if not processed_path.exists():
            logger.warning(f"Processed file {processed_path} not found. Running fallback check...")
            # Try to locate data/processed/knowledge_chunks.json
            alt_path = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "knowledge_chunks.json"
            if alt_path.exists():
                processed_path = alt_path

        if processed_path.exists():
            with open(processed_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            logger.info(f"Loaded {len(self.chunks)} knowledge chunks for retrieval.")
        else:
            logger.error("No knowledge chunks could be loaded!")
            self.chunks = []

        # Build Semantic Vector Index using Scikit-Learn TF-IDF N-gram representation
        if self.chunks:
            # Combine title, topic, variables, and text for rich contextual representation
            corpus = [
                f"{c.get('title', '')} {c.get('topic', '')} {' '.join(c.get('variables', []))} {c.get('text', '')}"
                for c in self.chunks
            ]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                stop_words="english",
                sublinear_tf=True
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            logger.info("Semantic vector index successfully trained and indexed.")

        # Attempt to initialize ChromaDB with custom fast local TF-IDF embedding function
        try:
            import chromadb
            from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

            class FastTfidfEmbedding(EmbeddingFunction):
                def __init__(self, vectorizer):
                    self.vectorizer = vectorizer
                def __call__(self, input: Documents) -> Embeddings:
                    arr = self.vectorizer.transform(input).toarray()
                    return arr.tolist()

            emb_fn = FastTfidfEmbedding(self.vectorizer)
            client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
            collection = client.get_or_create_collection(
                name="darukaa_biodiversity_knowledge",
                embedding_function=emb_fn,
                metadata={"hnsw:space": "cosine"}
            )
            # Populate if empty
            if collection.count() == 0 and self.chunks:
                ids = [c["chunk_id"] for c in self.chunks]
                documents = [f"{c['title']}\n{c['text']}" for c in self.chunks]
                metadatas = [
                    {
                        "organization": c["organization"],
                        "year": c["year"],
                        "topic": c["topic"],
                        "url": c.get("url", "")
                    }
                    for c in self.chunks
                ]
                collection.add(ids=ids, documents=documents, metadatas=metadatas)
            self.chroma_client = client
            self.chroma_collection = collection
            self.use_chroma = True
            logger.info("ChromaDB vector store connected and active with custom local embedding function.")
        except Exception as e:
            logger.info(f"ChromaDB local embedding setup exception: ({e}); utilizing built-in Scikit-Learn Cosine Vector Index.")

        self.initialized = True

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        variables_filter: Optional[List[str]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieves top_k relevant scientific chunks based on cosine similarity
        between the query and indexed literature.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Boost score if chunk matches target variables
        ranked_indices = np.argsort(similarities)[::-1]
        
        results: List[RetrievedChunk] = []
        for idx in ranked_indices:
            chunk = self.chunks[idx]
            raw_score = float(similarities[idx])
            
            # If variable filter applied, apply relevance boost or filter
            var_match = True
            if variables_filter:
                chunk_vars = chunk.get("variables", [])
                matching_vars = set(variables_filter).intersection(set(chunk_vars))
                if matching_vars:
                    raw_score = min(0.99, raw_score + 0.15 * len(matching_vars))
                else:
                    # slight demote if filtered and no overlap
                    raw_score = raw_score * 0.7

            # Base threshold to avoid completely irrelevant noise
            if raw_score < 0.05 and len(results) >= 2:
                continue

            results.append(
                RetrievedChunk(
                    chunk_id=chunk["chunk_id"],
                    source_id=chunk["source_id"],
                    title=chunk["title"],
                    organization=chunk["organization"],
                    year=chunk["year"],
                    url=chunk.get("url", ""),
                    topic=chunk["topic"],
                    text=chunk["text"],
                    score=round(raw_score, 4),
                    variables=chunk.get("variables", [])
                )
            )
            if len(results) >= top_k:
                break

        return results

    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Returns the bibliographic sources catalog."""
        catalog_path = settings.METADATA_CATALOG
        if catalog_path.exists():
            with open(catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("sources", [])
        # Fallback to unique chunks
        unique_sources = {}
        for c in self.chunks:
            sid = c.get("source_id", "")
            if sid not in unique_sources:
                unique_sources[sid] = {
                    "id": sid,
                    "title": c.get("title"),
                    "organization": c.get("organization"),
                    "year": c.get("year"),
                    "url": c.get("url"),
                    "topic": c.get("topic"),
                    "metrics": c.get("variables", [])
                }
        return list(unique_sources.values())


# Global singleton instance
vector_store = VectorStoreService()
