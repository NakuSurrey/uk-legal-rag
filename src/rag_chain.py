"""
Phase 2: RAG Chain — LLM Integration with Hugging Face Inference API
=====================================================================
This script connects  working ChromaDB (Phase 1) to a free LLM.
It retrieves relevant chunks and generates grounded, accurate answers.

"""

import os
import sys
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# Step 1: Load environment variables FIRST
# ─────────────────────────────────────────────
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    print("\n❌ ERROR: HUGGINGFACE_API_KEY not found in .env file.")
    print("   Fix: Open  .env file and add  key:")
    print("   HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("\n   Get  free key at: https://huggingface.co/settings/tokens")
    print("   Token type: 'Read' access is enough.\n")
    sys.exit(1)

os.environ["HF_TOKEN"] = HUGGINGFACE_API_KEY
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACE_API_KEY

print("✅ API key loaded from .env")

# ─────────────────────────────────────────────
# Step 2: Import libraries AFTER env check
# ─────────────────────────────────────────────
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient

# ─────────────────────────────────────────────
# Step 3: Connect to existing ChromaDB
# ─────────────────────────────────────────────
# CHROMA_PATH = "./chroma_db"

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

print("⏳ Loading vector database...")

try:
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function
    )
    collection = vectorstore._collection
    doc_count = collection.count()
    if doc_count == 0:
        print("\n❌ ERROR: ChromaDB is empty. Did  run Phase 1?")
        sys.exit(1)
    print(f"✅ ChromaDB loaded — {doc_count} chunks available")
except Exception as e:
    print(f"\n❌ ERROR: Could not load ChromaDB from '{CHROMA_PATH}'")
    print(f"   Details: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────
# Step 4: Set up the retriever
# ─────────────────────────────────────────────
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

print("✅ Retriever ready (top 4 chunks per query)")

# ─────────────────────────────────────────────
# Step 5: Initialize the Hugging Face LLM
# ─────────────────────────────────────────────
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

print(f"⏳ Connecting to Hugging Face model: {MODEL_ID}")

try:
    client = InferenceClient(
        model=MODEL_ID,
        token=HUGGINGFACE_API_KEY,
    )
    test_response = client.chat_completion(
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5,
    )
    print("✅ LLM connected and responding")
except Exception as e:
    print(f"\n❌ ERROR: Could not connect to Hugging Face API.")
    print(f"   Details: {e}")
    print("   Common fixes:")
    print("   1. Check  API key is correct in .env")
    print("   2. Check  internet connection")
    print("   3. The model may be loading (cold start — wait 60s and retry)\n")
    sys.exit(1)

# ─────────────────────────────────────────────
# Step 6: The Anti-Hallucination System Prompt
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """ are a UK legal and regulatory assistant.  job is to answer questions accurately using ONLY the provided context from official UK documents.

STRICT RULES:
1. ONLY use information from the CONTEXT below to answer.
2. If the answer is NOT in the context, reply exactly: "I cannot find this information in the provided documents. Please check the official UK government website at gov.uk for the most current guidance."
3. Do NOT make up laws, regulations, dates, or numbers.
4. Quote the relevant section when possible.
5. Keep answers concise and professional.
6. If the context is partially relevant, say what  CAN confirm and what  CANNOT."""

# ─────────────────────────────────────────────
# Step 7: Helper functions
# ─────────────────────────────────────────────

def format_docs(docs):
    """Turn retrieved Document objects into a single text block."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        formatted.append(
            f"[Source {i}: {source}, Page {page}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)

# ─────────────────────────────────────────────
# Step 8: Conversational Memory
# ─────────────────────────────────────────────
chat_history = []

def format_chat_history(history):
    """Convert chat history into messages for the chat API."""
    messages = []
    for human_msg, ai_msg in history[-5:]:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    return messages

# ─────────────────────────────────────────────
# Step 9: The main ask() function
# ─────────────────────────────────────────────
def ask(question: str) -> dict:
    """
    Ask a question about  UK regulatory documents.
    """
    try:
        # Step A: Retrieve relevant chunks
        retrieved_docs = retriever.invoke(question)

        if not retrieved_docs:
            return {
                "answer": "No relevant documents found in the database.",
                "sources": [],
                "num_chunks": 0
            }

        # Step B: Format context
        context_text = format_docs(retrieved_docs)

        # Step C: Build messages for chat API
        system_with_context = f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context_text}"

        messages = [{"role": "system", "content": system_with_context}]
        messages.extend(format_chat_history(chat_history))
        messages.append({"role": "user", "content": question})

        # Step D: Call the LLM
        response = client.chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.1,
            top_p=0.9,
        )

        # Step E: Extract the answer
        answer = response.choices[0].message.content.strip()

        # Step F: Update conversation memory
        chat_history.append((question, answer))

        # Step G: Prepare source info
        sources = []
        for doc in retrieved_docs:
            sources.append({
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "?"),
                "preview": doc.page_content[:100] + "..."
            })

        return {
            "answer": answer,
            "sources": sources,
            "num_chunks": len(retrieved_docs)
        }

    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__

        if "429" in error_msg or "rate" in error_msg.lower():
            return {
                "answer": "⚠️ Rate limit hit. Wait 60 seconds and try again.",
                "sources": [], "num_chunks": 0
            }
        elif "503" in error_msg or "loading" in error_msg.lower():
            return {
                "answer": "⏳ Model is loading (cold start). Wait 30-60s and retry.",
                "sources": [], "num_chunks": 0
            }
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return {
                "answer": "❌ API key invalid. Check HUGGINGFACE_API_KEY in .env.",
                "sources": [], "num_chunks": 0
            }
        else:
            return {
                "answer": f"❌ Unexpected error ({error_type}): {error_msg}",
                "sources": [], "num_chunks": 0
            }

# ─────────────────────────────────────────────
# Step 10: Interactive Terminal Chat Loop
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  UK Legal Document Assistant — Phase 2 Test")
    print("  Type  questions below. Type 'quit' to exit.")
    print("  Type 'sources' to see what chunks were used.")
    print("  Type 'clear' to reset conversation memory.")
    print("=" * 60 + "\n")

    last_result = None

    while True:
        try:
            user_input = input("📝 : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\nGoodbye! 👋")
            break

        if user_input.lower() == "clear":
            chat_history.clear()
            print("🗑️  Conversation memory cleared.\n")
            continue

        if user_input.lower() == "sources":
            if last_result and last_result["sources"]:
                print("\n📚 Sources used in last answer:")
                for i, src in enumerate(last_result["sources"], 1):
                    print(f"   [{i}] {src['source']} (Page {src['page']})")
                    print(f"       Preview: {src['preview']}")
                print()
            else:
                print("   No sources available. Ask a question first.\n")
            continue

        print("⏳ Thinking...")
        result = ask(user_input)
        last_result = result

        print(f"\n🤖 Assistant: {result['answer']}")
        print(f"   (Used {result['num_chunks']} chunks from  documents)\n")
