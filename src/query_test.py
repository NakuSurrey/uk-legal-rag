"""
PHASE 1 - SCRIPT 4: QUERY TEST (THE MILESTONE!)
==================================================
What this does:
    Lets you type a question and retrieves the 3 most relevant 
    paragraphs from your vector database.
    
    This is YOUR MILESTONE: if this works, Phase 1 is COMPLETE.

How to test:
    1. Make sure you've already run Script 3 (vectorstore.py) to build the database.
    2. From your PROJECT ROOT folder, run:
       python src/query_test.py
    3. Type a question like: "What are the changes to zero hours contracts?"
    4. You should see 3 relevant paragraphs from your PDF!

What to try:
    - "What changes affect sick pay?"
    - "When do the employment rights changes take effect?"
    - "What happens with unfair dismissal?"
    - "What are the plans for flexible working?"
    - Type 'quit' to exit.

After this works: COMMIT TO GIT! Then you're ready for Phase 2.
    git add .
    git commit -m "Phase 1 complete: PDF parsing, chunking, and vector search working"
    git push origin master
"""

from vectorstore import load_vectorstore
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def search(vectorstore, query: str, num_results: int = 3):
    """
    Searches the vector database and returns the most relevant chunks.
    
    Args:
        vectorstore: The ChromaDB vector store
        query: The user's question (plain English)
        num_results: How many chunks to return (default: 3)
    
    Returns:
        List of (Document, score) tuples, sorted by relevance.
        Lower score = more relevant (it's a distance metric).
    """

    # similarity_search_with_score returns both the document AND a relevance score
    results = vectorstore.similarity_search_with_score(query, k=num_results)

    return results


def main():
    print("=" * 60)
    print("PHASE 1 - MILESTONE TEST: QUERY YOUR DOCUMENTS")
    print("=" * 60)
    print()

    # Load the existing database
    print("Loading vector database...")
    try:
        vectorstore = load_vectorstore()
    except FileNotFoundError as e:
        print(str(e))
        print("\nRun 'python src/vectorstore.py' first to build the database.")
        return

    count = vectorstore._collection.count()
    print(f"Database loaded with {count} chunks.")
    print()
    print("Type a question about your UK regulatory documents.")
    print("Type 'quit' to exit.")
    print("-" * 60)

    while True:
        print()
        query = input("Your question: ").strip()

        if not query:
            continue

        if query.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Phase 1 is complete if you saw relevant results above.")
            print("Now commit your work:")
            print('  git add .')
            print('  git commit -m "Phase 1 complete: PDF parsing, chunking, vector search"')
            print('  git push origin master')
            break

        # Search the database
        results = search(vectorstore, query)

        print()
        print(f"Top {len(results)} results for: \"{query}\"")
        print("-" * 60)

        for i, (doc, score) in enumerate(results):
            print(f"\n{'='*40}")
            print(f"  RESULT {i + 1}  |  Relevance Score: {score:.4f}")
            print(f"  (Lower score = more relevant)")
            print(f"{'='*40}")
            print()
            print(doc.page_content)
            print()

        print("-" * 60)
        print("Ask another question or type 'quit' to exit.")


if __name__ == "__main__":
    main()
