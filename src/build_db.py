"""
Phase 5: Pre-populate ChromaDB during Docker build.
This runs once during 'docker build' so the container starts ready to serve queries.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_loader import load_all_pdfs
from chunker import chunk_text
from vectorstore import create_vectorstore

def build():
    # Resolve the data/ folder relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")

    print(f"Loading PDFs from {data_dir}...")
    text = load_all_pdfs(data_dir)
    print(f"Loaded {len(text):,} characters")

    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    create_vectorstore(chunks, force_rebuild=True)
    print("ChromaDB populated successfully!")

if __name__ == "__main__":
    build()