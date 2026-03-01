# Phase 2: LLM Integration with Hugging Face — Complete Guide

## What You Just Built

`src/rag_chain.py` is the **brain** of your RAG pipeline. It:
1. Opens your ChromaDB (the filing cabinet from Phase 1)
2. Takes a user's question
3. Retrieves the 4 most relevant chunks
4. Feeds them to Mistral-7B-Instruct via the **free** Hugging Face Inference API
5. Returns a grounded, fact-checked answer
6. Remembers the conversation (up to 5 exchanges)

---

## Before You Run: Setup Checklist

### 1. Get Your Free Hugging Face API Key

1. Go to: https://huggingface.co/settings/tokens
2. Create account if needed (free)
3. Click **"New token"**
4. Name: `uk-legal-rag` (or anything)
5. Type: **Read** (that's all you need)
6. Copy the token (starts with `hf_`)

### 2. Add the Key to Your .env File

Open your `.env` file and paste:

```
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=
```

> ⚠️ **TRAP AVOIDED:** Never put the key directly in your Python code. The `.env` file is in your `.gitignore`, so it will never be uploaded to GitHub.

### 3. Install One New Library (If Needed)

Your Phase 0 `requirements.txt` should already include `langchain-huggingface`. If you get an import error, run:

```bash
pip install langchain-huggingface huggingface_hub
pip freeze > requirements.txt
```

### 4. Copy the Script

Copy `rag_chain.py` into your `src/` folder:

```
uk-legal-rag/
├── src/
│   ├── pdf_loader.py      ← Phase 1
│   ├── chunker.py         ← Phase 1
│   ├── vectorstore.py     ← Phase 1
│   ├── query_test.py      ← Phase 1
│   └── rag_chain.py       ← Phase 2 (NEW)
├── chroma_db/             ← Your embedded chunks from Phase 1
├── data/                  ← Your PDFs
└── .env                   ← Your API key
```

---

## How to Run

```bash
# 1. Make sure you're in your project root folder
cd /c/development/vibe\ coding/project

# 2. Activate venv (check for (venv) in terminal)
source venv/Scripts/activate

# 3. Run the script
python src/rag_chain.py
```

You should see:
```
✅ API key loaded from .env
⏳ Loading vector database...
✅ ChromaDB loaded — 32 chunks available
⏳ Connecting to Hugging Face model: mistralai/Mistral-7B-Instruct-v0.3
✅ LLM connected

============================================================
  UK Legal Document Assistant — Phase 2 Test
  Type your questions below. Type 'quit' to exit.
  Type 'sources' to see what chunks were used.
  Type 'clear' to reset conversation memory.
============================================================

📝 You: 
```

---

## Test Questions to Try

Start with these to verify everything works:

1. **Direct factual question:** "What are the working hour limits in the UK?"
2. **Follow-up (tests memory):** "Does this apply to workers under 18?"
3. **Out-of-scope (tests anti-hallucination):** "What is the capital of France?"
   - Expected: Should say it cannot find this in the documents.
4. **Type `sources`** — to see which exact chunks were used.

---

## Troubleshooting

### "Model is loading" / 503 error
**What happened:** Free tier models go to sleep after ~15 min of inactivity. First request wakes them up.
**Fix:** Wait 30-60 seconds, then try again. This is normal on the free tier.

### "Rate limit" / 429 error
**What happened:** Free tier limits you to ~30 requests per hour.
**Fix:** Wait 60 seconds. For development, this is plenty. For the live demo (Phase 5), consider upgrading to Hugging Face Pro ($9/month) or switching to OpenAI.

### "401 Unauthorized"
**What happened:** API key is wrong or expired.
**Fix:** Go to https://huggingface.co/settings/tokens, create a new token, paste it in `.env`.

### Answer quality is poor / model echoes the prompt
**What happened:** Some HF models need prompt formatting tweaks.
**Fix:** The script includes `answer.strip()` cleanup. If the model adds junk, you can add more cleanup in the `ask()` function. This is normal with free models — OpenAI models don't have this issue.

### ChromaDB errors
**What happened:** The `chroma_db/` folder is missing or corrupted.
**Fix:** Re-run your Phase 1 vectorstore.py script to rebuild it.

---

## Architecture: Why This Script Is Built This Way

### The `ask()` function returns a dict, not just a string
```python
{"answer": "...", "sources": [...], "num_chunks": 4}
```
**Why:** In Phase 3 (FastAPI), you'll call `ask(question)` from your API endpoint and return this dict as JSON. In Phase 4 (Streamlit), you'll use `result["answer"]` for the chat bubble and `result["sources"]` for a collapsible "View Sources" panel. Building it as a clean function now means zero rewriting later.

### Chat history is a plain list, not LangChain Memory
**Why:** LangChain's `ConversationBufferMemory` class has version compatibility issues and doesn't serialize well for APIs. A simple list of `(question, answer)` tuples is easier to debug, easier to send over HTTP, and works identically.

### History is limited to last 5 exchanges
**Why:** Each exchange gets injected into the prompt. Too much history = too many tokens = slower responses and higher costs. 5 exchanges is plenty for natural follow-up questions.

### Error handling catches specific HTTP codes
**Why:** Free tier HF has three common failure modes (cold start, rate limit, bad key). Instead of a generic "something went wrong," the user gets an actionable fix message.

---

## Commit Your Progress

After the script works:

```bash
git add .
git commit -m "Phase 2: LLM integration with Hugging Face Inference API"
git push origin master
```

---

## Free Tier Limitations to Know

| Feature              | Free Tier          | Pro ($9/mo)        |
|----------------------|--------------------|--------------------|
| Rate limit           | ~30 req/hour       | Higher             |
| Cold starts          | 30-60 sec wait     | Faster             |
| Model access         | Most open models   | All models         |
| Response speed       | Variable           | More consistent    |

**For development and testing:** Free tier is perfect.
**For your live deployed demo (Phase 5):** Consider Pro or switching to OpenAI ($5 credit for new accounts).

---

## What's Next: Phase 3

Phase 3 wraps your `ask()` function in a FastAPI server so it can receive web requests. Your starting message for Phase 3:

> Phase 2 complete — `src/rag_chain.py` works in the terminal. I can ask questions about my UK regulatory PDF and get grounded answers from Mistral-7B via the free HF Inference API. Conversation memory works. Anti-hallucination prompt works. Ready for Phase 3: wrapping the `ask()` function in a FastAPI endpoint.
