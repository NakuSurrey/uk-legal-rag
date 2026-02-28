"""
PHASE 1 - SCRIPT 2: TEXT CHUNKER
==================================
What this does:
    Takes the text from your PDF and splits it into overlapping chunks.
    
Why chunk?
    - You can't send a whole 12-page document to an AI at once (too expensive, too slow).
    - Instead, you chop it into bite-sized paragraphs (~1000 characters each).
    - Overlap (200 chars) ensures no sentence gets cut in half between two chunks.

How to test:
    1. Make sure your venv is activated
    2. From your PROJECT ROOT folder, run:
       python src/chunker.py
    3. You should see numbered chunks printed in the terminal.

If it works: Move on to Script 3 (vectorstore.py)
"""

# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdf_loader import load_all_pdfs  # Import our Script 1
import sys
import os

# Add the src directory to the Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Splits a big string of text into smaller overlapping chunks.
    
    Args:
        text: The full text extracted from PDFs
        chunk_size: Max characters per chunk (1000 is a good default)
        chunk_overlap: How many characters overlap between chunks (200 prevents cut sentences)
    
    Returns:
        A list of LangChain Document objects (each has .page_content and .metadata)
    
    Why RecursiveCharacterTextSplitter?
        - It tries to split at natural breakpoints: paragraphs first, then sentences, 
          then words, and only as a last resort, mid-word.
        - This preserves meaning much better than a dumb character count split.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,  # Measure chunk size by character count
        separators=["\n\n", "\n", ". ", " ", ""]  # Try these split points in order
    )

    # create_documents takes a list of strings and returns Document objects
    chunks = splitter.create_documents([text])

    return chunks


# =============================================================
# TEST: Run this script directly to see your chunks
# =============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 - SCRIPT 2: TEXT CHUNKER TEST")
    print("=" * 60)
    print()

    # Step 1: Load the PDF text (reusing Script 1)
    print("Step 1: Loading PDF text...")
    text = load_all_pdfs("data")

    # Step 2: Chunk it
    print("\nStep 2: Chunking text...")
    chunks = chunk_text(text)

    print(f"\n  Total chunks created: {len(chunks)}")
    print(f"  Average chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks)} characters")

    # Show first 3 chunks as a preview
    print()
    print("-" * 60)
    print("PREVIEW: First 3 chunks")
    print("-" * 60)

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- CHUNK {i + 1} ({len(chunk.page_content)} chars) ---")
        print(chunk.page_content[:500])  # Show first 500 chars of each chunk
        print("...")

    print()
    print("-" * 60)
    print(f"SUCCESS! Created {len(chunks)} chunks from your PDF.")
    print("If the chunks look like readable paragraphs, move to Script 3.")
    print("-" * 60)
