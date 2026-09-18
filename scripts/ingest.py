"""
Ingestion script for Darukaa.Earth Biodiversity Knowledge Base.
Processes authentic raw scientific documents into structured chunks with metadata,
generates semantic representations, and persists the vector index.
"""

import os
import json
import glob
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_FILE = PROCESSED_DIR / "knowledge_chunks.json"


def chunk_document(doc: dict) -> list[dict]:
    """
    Extracts atomic scientific chunks with rich metadata from a raw document.
    Ensures every chunk preserves origin, organization, year, variables, and quantitative evidence.
    """
    chunks = []
    content = doc.get("content", "")
    base_id = doc.get("id", "doc")
    
    # Split on paragraph or sentences if content is lengthy (> 450 chars)
    sentences = [s.strip() for s in content.split(". ") if s.strip()]
    
    # We create structured cohesive chunks (2-3 sentences max or logical blocks)
    current_chunk = []
    chunk_index = 1
    current_length = 0
    
    for sentence in sentences:
        s_with_dot = sentence if sentence.endswith(".") else sentence + "."
        current_chunk.append(s_with_dot)
        current_length += len(s_with_dot)
        
        if current_length >= 300:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "chunk_id": f"{base_id}_c{chunk_index}",
                "source_id": base_id,
                "title": doc.get("title", ""),
                "organization": doc.get("organization", ""),
                "authors": doc.get("authors", ""),
                "year": doc.get("year", 2020),
                "url": doc.get("doi_or_url", ""),
                "topic": doc.get("topic", ""),
                "ecosystem_types": doc.get("ecosystem_types", []),
                "variables": doc.get("variables", []),
                "text": chunk_text,
                "quantitative_ranges": doc.get("quantitative_ranges", {})
            })
            current_chunk = []
            current_length = 0
            chunk_index += 1
            
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            "chunk_id": f"{base_id}_c{chunk_index}",
            "source_id": base_id,
            "title": doc.get("title", ""),
            "organization": doc.get("organization", ""),
            "authors": doc.get("authors", ""),
            "year": doc.get("year", 2020),
            "url": doc.get("doi_or_url", ""),
            "topic": doc.get("topic", ""),
            "ecosystem_types": doc.get("ecosystem_types", []),
            "variables": doc.get("variables", []),
            "text": chunk_text,
            "quantitative_ranges": doc.get("quantitative_ranges", {})
        })
        
    return chunks


def run_ingestion():
    print(f"[Ingestion] Scanning raw data directory: {RAW_DIR}")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    all_chunks = []
    raw_files = list(RAW_DIR.glob("*.json"))
    print(f"[Ingestion] Found {len(raw_files)} raw knowledge files.")
    
    for file_path in raw_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                docs = json.load(f)
                if isinstance(docs, dict):
                    docs = [docs]
                for doc in docs:
                    chunks = chunk_document(doc)
                    all_chunks.extend(chunks)
                    print(f"  -> Ingested: '{doc.get('title')}' -> {len(chunks)} chunks")
        except Exception as e:
            print(f"[Error] Failed to process {file_path.name}: {e}")
            
    print(f"[Ingestion] Total generated scientific chunks: {len(all_chunks)}")
    
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"[Ingestion] Saved processed chunks to: {PROCESSED_FILE}")
    return all_chunks


if __name__ == "__main__":
    run_ingestion()
