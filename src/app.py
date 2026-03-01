"""
Phase 4: Streamlit Chat UI for UK Legal RAG Pipeline
=====================================================
This is the "face" of the application — the web interface recruiters will click.
It sends questions to the FastAPI backend (/ask endpoint) and displays answers
in a professional chat format.

"""

import streamlit as st
import requests
import time
import os

# ============================================================
# CONFIGURATION
# ============================================================
# Where  FastAPI server is running
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title="UK Legal Document Assistant",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS — Makes it look professional, not like a homework assignment
# ============================================================
st.markdown("""
<style>
    /* Disclaimer banner */
    .disclaimer {
        background-color: #FFF3CD;
        border: 1px solid #FFECB5;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 20px;
        font-size: 0.85em;
        color: #664D03;
    }

    /* Sources expander styling */
    .source-chunk {
        background-color: #F8F9FA;
        border-left: 3px solid #0D6EFD;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 6px 6px 0;
        font-size: 0.85em;
        color: #333;
    }

    /* Status indicator */
    .status-connected {
        color: #198754;
        font-weight: 600;
    }
    .status-disconnected {
        color: #DC3545;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("⚖️ UK Legal RAG")
    st.caption("Intelligent Document Q&A System")

    st.divider()

    # Backend health check
    st.subheader("System Status")
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            st.markdown('<p class="status-connected">● Backend Connected</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-disconnected">● Backend Error</p>', unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.markdown('<p class="status-disconnected">● Backend Offline</p>', unsafe_allow_html=True)
        st.error("FastAPI server is not running. Start it with:\n\n`cd src && python api.py`")

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # About section
    st.subheader("About")
    st.markdown(
        "This AI assistant answers questions about **UK employment regulations** "
        "using Retrieval-Augmented Generation (RAG). It retrieves relevant passages "
        "from official UK government documents and generates grounded answers."
    )

    st.divider()

    # Show/hide sources toggle
    st.session_state.show_sources = st.toggle("Show source documents", value=True)

# ============================================================
# MAIN CHAT AREA
# ============================================================

# Header
st.title("UK Legal Document Assistant")
st.markdown(
    '<div class="disclaimer">'
    '⚠️ <strong>Disclaimer:</strong> This is an AI prototype for academic purposes. '
    'It does not provide legal advice. Always consult official '
    '<a href="https://www.gov.uk" target="_blank">UK government guidelines</a>.'
    '</div>',
    unsafe_allow_html=True,
)

# ============================================================
# HELPER: Clean up source display
# ============================================================
# The ask() function in rag_chain.py returns sources as dicts like:
#   {'source': 'Unknown', 'page': '?', 'preview': 'actual text here...'}
# or sometimes as string representations of dicts.
# This function extracts just the readable preview text.

def clean_source(source):
    """Extract clean, readable text from a source object (dict, string, or raw text)."""
    if isinstance(source, dict):
        preview = source.get("preview", source.get("page_content", str(source)))
        return preview.strip()

    # If it's a string that looks like a dict, try to extract the preview
    source_str = str(source)
    if source_str.startswith("{") and "'preview':" in source_str:
        try:
            import ast
            parsed = ast.literal_eval(source_str)
            if isinstance(parsed, dict):
                return parsed.get("preview", source_str).strip()
        except (ValueError, SyntaxError):
            pass

    if hasattr(source, "page_content"):
        return source.page_content.strip()

    return source_str.strip()


# ============================================================
# SESSION STATE — Keeps chat history alive across Streamlit reruns
# ============================================================
# THE TRAP AVOIDED: Streamlit re-runs the ENTIRE script top-to-bottom
# every time the user interacts with anything. Without session_state,
# the chat history would vanish after every message.

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# DISPLAY EXISTING CHAT HISTORY
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources if they exist and toggle is on
        if message["role"] == "assistant" and "sources" in message and st.session_state.show_sources:
            if message["sources"]:
                with st.expander(f"📄 View {len(message['sources'])} source(s) used"):
                    for i, source in enumerate(message["sources"], 1):
                        clean = clean_source(source)
                        st.markdown(
                            f'<div class="source-chunk"><strong>Source {i}:</strong><br>{clean}</div>',
                            unsafe_allow_html=True,
                        )

# ============================================================
# CHAT INPUT & API CALL
# ============================================================
if prompt := st.chat_input("Ask a question about UK employment regulations..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the FastAPI backend and display the response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": prompt},
                    timeout=120,  # LLM on free tier can be slow (30-60s cold start)
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer received.")
                    sources = data.get("sources", [])
                    num_chunks = data.get("num_chunks", 0)

                    # Display the answer
                    st.markdown(answer)

                    # Display sources if toggle is on
                    if sources and st.session_state.show_sources:
                        with st.expander(f"📄 View {len(sources)} source(s) used"):
                            for i, source in enumerate(sources, 1):
                                clean = clean_source(source)
                                st.markdown(
                                    f'<div class="source-chunk"><strong>Source {i}:</strong><br>{clean}</div>',
                                    unsafe_allow_html=True,
                                )

                    # Save to session state (including sources for history display)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                else:
                    error_msg = f"⚠️ Server returned status code {response.status_code}. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.exceptions.ConnectionError:
                error_msg = (
                    "❌ **Cannot connect to the backend server.**\n\n"
                    "Make sure FastAPI is running:\n"
                    "```\ncd src && python api.py\n```"
                )
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.exceptions.Timeout:
                error_msg = (
                    "⏰ **Request timed out.** The LLM may be experiencing a cold start. "
                    "This is normal on the free Hugging Face tier — please wait 30 seconds and try again."
                )
                st.warning(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except Exception as e:
                error_msg = f"⚠️ Unexpected error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
