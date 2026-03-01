"""
PHASE 1 - SCRIPT 1: PDF LOADER
================================
What this does:
    Reads a PDF file from  data/ folder and extracts all the text.

How to test:
    1. Make sure  venv is activated ( see (venv) in terminal)
    2. From  PROJECT ROOT folder (uk-legal-rag), run:
       python src/pdf_loader.py
    3.  should see the text from  PDF printed in the terminal.

If it works: Move on to Script 2 (chunker.py)
If it fails: Check the error message — most likely the file path is wrong.
"""

import fitz  # This is PyMuPDF — the library is called 'fitz' internally
import os


def load_pdf(file_path: str) -> str:
    """
    Takes a PDF file path and returns ALL the text as one big string.

    Why PyMuPDF (fitz) instead of PyPDF2?
    - PyMuPDF handles tables, columns, and complex lats much better.
    - PyPDF2 often scrambles text from government documents.
    """

    # Safety check: does the file actually exist?
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"ERROR: Could not find the file at: {file_path}\n"
            f"Make sure the PDF is in  data/ folder and the name matches exactly."
        )

    # Open the PDF
    doc = fitz.open(file_path)

    # Extract text from every page and join them together
    all_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()  # Extracts text from this single page
        all_text += page_text + "\n"  # Add a newline between pages

    doc.close()

    return all_text


def load_all_pdfs(data_folder: str = "data") -> str:
    """
    Reads ALL PDFs in the data/ folder and combines their text.
    This way  can drop multiple PDFs in later without changing code.
    """

    if not os.path.exists(data_folder):
        raise FileNotFoundError(
            f"ERROR: The '{data_folder}' folder does not exist.\n"
            f"Make sure 're running this from  project root folder (uk-legal-rag)."
        )

    all_text = ""
    pdf_count = 0

    for filename in sorted(os.listdir(data_folder)):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(data_folder, filename)
            print(f"  Reading: {filename}...")
            text = load_pdf(file_path)
            all_text += text + "\n"
            pdf_count += 1

    if pdf_count == 0:
        raise FileNotFoundError(
            f"ERROR: No PDF files found in the '{data_folder}' folder.\n"
            f"Make sure  PDF is in the data/ folder and ends with .pdf"
        )

    print(f"\n  Successfully loaded {pdf_count} PDF(s).")
    return all_text


# =============================================================
# THIS PART ONLY RUNS WHEN  TEST THIS SCRIPT DIRECTLY
# It will NOT run when other scripts import from this file.
# =============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 - SCRIPT 1: PDF LOADER TEST")
    print("=" * 60)
    print()

    text = load_all_pdfs("data")

    # Show a preview (first 2000 characters)
    print()
    print("-" * 60)
    print("PREVIEW OF EXTRACTED TEXT (first 2000 chars):")
    print("-" * 60)
    print(text[:2000])
    print()
    print("-" * 60)
    print(f"TOTAL CHARACTERS EXTRACTED: {len(text):,}")
    print(f"TOTAL WORDS (approx): {len(text.split()):,}")
    print("-" * 60)
    print()
    print("SUCCESS! If  can see readable text above, move to Script 2.")
    print("If the text looks like gibberish,  PDF might be scanned (image-based).")
