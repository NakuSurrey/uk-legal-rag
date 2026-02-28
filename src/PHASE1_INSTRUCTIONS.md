# Phase 1: PDF Parsing & Vectorization — Step-by-Step Instructions

## Setup

1. Copy all 4 `.py` files into your `src/` folder:
   - `pdf_loader.py`
   - `chunker.py`
   - `vectorstore.py`
   - `query_test.py`

2. Your folder should now look like:
   ```
   uk-legal-rag/
   ├── data/
   │   └── employment_rights_roadmap.pdf
   ├── src/
   │   ├── pdf_loader.py      ← NEW
   │   ├── chunker.py         ← NEW
   │   ├── vectorstore.py     ← NEW
   │   └── query_test.py      ← NEW
   ├── notebooks/
   ├── tests/
   ├── venv/
   ├── .env
   ├── .gitignore
   └── requirements.txt
   ```

---

## Running the Scripts (DO THEM IN ORDER)

**IMPORTANT:** Always run from your PROJECT ROOT folder (uk-legal-rag), NOT from inside src/.

### Before anything: Activate your venv!
```bash
source venv/Scripts/activate
```
Check for `(venv)` in your terminal.

---

### Script 1: Test PDF Loading
```bash
python src/pdf_loader.py
```
**Expected:** You see readable text from your PDF printed in the terminal.  
**If it fails:** Check that your PDF is in the `data/` folder and the name ends with `.pdf`.

---

### Script 2: Test Chunking
```bash
python src/chunker.py
```
**Expected:** You see "Total chunks created: XX" and 3 sample chunks of readable text.  
**If it fails:** Script 1 probably has an issue. Fix Script 1 first.

---

### Script 3: Build the Vector Database (SLOW FIRST TIME)
```bash
python src/vectorstore.py
```
**Expected (first run):**
- Downloads a ~90MB model (needs internet, takes 1-3 mins)
- Creates the `chroma_db/` folder in your project root
- Shows "Database created with X chunks"
- Shows a quick sanity check search result

**Expected (subsequent runs):**
- Detects existing database, loads it instantly
- To force a fresh rebuild: change `force_rebuild=True` in the code

**If it fails with "ModuleNotFoundError":**  
Make sure your venv is activated and run: `pip install sentence-transformers`

---

### Script 4: THE MILESTONE TEST
```bash
python src/query_test.py
```
**Try these questions:**
- "What are the changes to zero hours contracts?"
- "What changes affect sick pay?"
- "When do the employment rights changes take effect?"
- "What happens with unfair dismissal?"

**Expected:** For each question, you see 3 relevant paragraphs from your PDF!

Type `quit` to exit.

---

## After the Milestone: COMMIT TO GIT!

```bash
git add .
git commit -m "Phase 1 complete: PDF parsing, chunking, vector search"
git push origin master
```

**Verify on GitHub:** Check that `chroma_db/` and `.env` are NOT visible in your repo.
(They should be hidden by `.gitignore`)

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'fitz'` | `pip install pymupdf` |
| `ModuleNotFoundError: No module named 'langchain'` | `pip install langchain langchain-community langchain-chroma` |
| `ModuleNotFoundError: No module named 'sentence_transformers'` | `pip install sentence-transformers` |
| `FileNotFoundError: data/ folder` | You're running from the wrong directory. `cd` to your project root. |
| `No PDF files found` | Make sure the file ends with `.pdf` (not `.PDF` or `.pdf.pdf`) |
| Script 2/3/4 can't import from Script 1 | You're running from inside `src/`. Run from the project root instead. |

---

## What You Just Built (The "Lego Bricks")

```
pdf_loader.py  →  Reads PDF files, outputs raw text
     ↓
chunker.py     →  Splits text into overlapping paragraphs
     ↓
vectorstore.py →  Converts paragraphs to math (vectors), saves to database
     ↓
query_test.py  →  Searches the database with your questions
```

Each brick works independently. If chunker.py breaks, pdf_loader.py is still safe.

---

## Ready for Phase 2?

Once the milestone test works, start a new chat with this message:

> Phase 1 is complete. I can load PDFs, chunk them, embed them with Hugging Face 
> (all-MiniLM-L6-v2) into ChromaDB, and search them with similarity queries.
> I'm ready for Phase 2: connecting the LLM to generate actual answers from 
> the retrieved chunks. I'm using Hugging Face (free, local). My setup: 
> Python 3.10.7, Git Bash on Windows, venv active, all libraries installed.
