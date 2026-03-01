"""
PHASE 1 - SCRIPT 3: VECTOR STORE (Embedding + ChromaDB)
=========================================================
What this does:
    Takes  text chunks, converts them into mathematical vectors (embeddings)
    using a FREE Hugging Face model that runs locally on  machine,
    and saves them into a ChromaDB database on  hard drive.
"""

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from pdf_loader import load_all_pdfs
from chunker import chunk_text
import os
import sys
import shutil

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# === CONFIGURATION ===
# Where to save the database on  hard drive
# CHROMA_DB_DIR = "chroma_db"

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

# The Hugging Face model for embeddings (free, runs locally)
# "all-MiniLM-L6-v2" is small (~90MB), fast, and very good quality
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embedding_function():
    """
    Creates the embedding function using Hugging Face.
    
    First time: Downloads the model from the internet (~90MB).
    After that: Uses the cached version from  machine (no internet needed).
    """
    print("  Loading Hugging Face embedding model...")
    print("  (First run downloads ~90MB model. After that, it's instant.)")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},  # Use CPU (works on any machine)
        encode_kwargs={"normalize_embeddings": True}  # Better search results
    )

    print("  Embedding model loaded!")
    return embeddings


def create_vectorstore(chunks: list, force_rebuild: bool = False):
    """
    Takes text chunks and stores them as vectors in ChromaDB.
    
    Args:
        chunks: List of LangChain Document objects (from chunker.py)
        force_rebuild: If True, deletes old database and rebuilds from scratch.
                      If False, skips if database already exists (saves time + money).
    
    Returns:
        A ChromaDB vector store object  can search.
    
    TRAP AVOIDED:  used persist_directory so the database saves to  hard drive.
    Without this, the database lives in RAM and disappears when close the terminal.
    'd have to re-embed everything (slow + wasteful) every time  restart.
    """

    # Check if database already exists
    if os.path.exists(CHROMA_DB_DIR) and not force_rebuild:
        print(f"\n  Database already exists at '{CHROMA_DB_DIR}/'.")
        print("  Loading existing database (no re-embedding needed)...")
        embeddings = get_embedding_function()
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )
        count = vectorstore._collection.count()
        print(f"  Loaded database with {count} chunks.")
        return vectorstore

    # If force_rebuild, delete the old database first
    if os.path.exists(CHROMA_DB_DIR) and force_rebuild:
        print(f"\n  Deleting old database at '{CHROMA_DB_DIR}/'...")
        shutil.rmtree(CHROMA_DB_DIR)

    # Create the embedding function
    embeddings = get_embedding_function()

    # Create the vector store and embed all chunks
    # This is the slow part — it converts every chunk into a vector
    print(f"\n  Embedding {len(chunks)} chunks into ChromaDB...")
    print("  This may take a minute or two...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

    count = vectorstore._collection.count()
    print(f"\n  Database created with {count} chunks at '{CHROMA_DB_DIR}/'.")
    return vectorstore


def load_vectorstore():
    """
    Loads an EXISTING vector store from disk.
    when already built the database and just want to search it.
    """
    if not os.path.exists(CHROMA_DB_DIR):
        raise FileNotFoundError(
            f"ERROR: No database found at '{CHROMA_DB_DIR}/'.\n"
            f"Run 'python src/vectorstore.py' first to create it."
        )

    embeddings = get_embedding_function()
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    return vectorstore


# =============================================================
# TEST: Run this script directly to build the database
# =============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 - SCRIPT 3: VECTOR STORE BUILDER")
    print("=" * 60)
    print()

    # Step 1: Load PDFs
    print("Step 1: Loading PDF text...")
    text = load_all_pdfs("data")

    # Step 2: Chunk the text
    print("\nStep 2: Chunking text...")
    chunks = chunk_text(text)
    print(f"  Created {len(chunks)} chunks.")

    # Step 3: Embed and store
    # force_rebuild=True so it always creates a fresh database when  test
    print("\nStep 3: Embedding chunks and building database...")
    vectorstore = create_vectorstore(chunks, force_rebuild=True)

    # Quick sanity check: search for something
    print()
    print("-" * 60)
    print("QUICK SANITY CHECK: Searching for 'employment rights'...")
    print("-" * 60)

    results = vectorstore.similarity_search("employment rights", k=2)

    for i, result in enumerate(results):
        print(f"\n--- Result {i + 1} ---")
        print(result.page_content[:300])
        print("...")

    print()
    print("-" * 60)
    print("SUCCESS!  vector database is built and searchable.")
    print(f"Database saved at: {CHROMA_DB_DIR}/")
    print("Move on to Script 4 (query_test.py) for the MILESTONE TEST!")
    print("-" * 60)
