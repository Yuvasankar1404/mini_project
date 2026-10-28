import os
import sys

# Prevent Windows OSError [Errno 22] on sys.stderr.flush in background/headless streams
os.environ["TQDM_DISABLE"] = "1"
if hasattr(sys.stderr, "flush"):
    _orig_stderr_flush = sys.stderr.flush
    def _safe_stderr_flush():
        try:
            _orig_stderr_flush()
        except OSError:
            pass
    sys.stderr.flush = _safe_stderr_flush

import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Set page config with modern theme
st.set_page_config(
    page_title="Researcher Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

from rag import process_urls, process_documents, generate_answer

# Inject Impressive 3D & Clean UI Stylesheet
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #151e36 0%, #0a0e1a 60%, #06080f 100%);
        color: #f1f5f9;
    }

    /* Block Container Padding */
    .block-container {
        max-width: 1050px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* 3D Header Card */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, rgba(30, 41, 69, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 40px -15px rgba(0, 0, 0, 0.6),
            0 0 0 1px rgba(99, 102, 241, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(16px);
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%);
        pointer-events: none;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 9999px;
        padding: 0.35rem 0.9rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #a5b4fc;
        margin-bottom: 0.9rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    }

    .hero-title {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin: 0 0 0.5rem 0 !important;
        letter-spacing: -0.02em;
        text-shadow: 0 4px 20px rgba(99, 102, 241, 0.25);
    }

    .hero-sub {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
        line-height: 1.5;
    }

    /* 3D Elevated Tabs */
    div[data-baseweb="tab-list"] {
        background: rgba(13, 19, 33, 0.75) !important;
        padding: 6px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4), 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        gap: 8px !important;
    }

    div[data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
        background: transparent !important;
    }

    div[data-baseweb="tab"]:hover {
        color: #f8fafc !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }

    div[aria-selected="true"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
        box-shadow: 
            0 4px 14px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    }

    div[data-baseweb="tab-border"] {
        display: none !important;
    }

    div[data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .section-title span.icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(79, 70, 229, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
    }

    /* 3D Inputs (Debossed / Inset depth) */
    .stTextInput > div > div > input {
        background: #090e1a !important;
        color: #f8fafc !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        box-shadow: 
            inset 0 3px 6px rgba(0, 0, 0, 0.5),
            0 1px 0 rgba(255, 255, 255, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.4),
            0 0 0 3px rgba(99, 102, 241, 0.25),
            0 4px 12px rgba(99, 102, 241, 0.15) !important;
    }

    /* 3D Tactile Buttons */
    .stButton > button {
        background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.8rem !important;
        border: none !important;
        border-bottom: 4px solid #3730a3 !important;
        box-shadow: 
            0 8px 18px -2px rgba(79, 70, 229, 0.45),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transform: translateY(0) !important;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #6d70ff 0%, #5850ec 100%) !important;
        transform: translateY(-2px) !important;
        border-bottom: 5px solid #312e81 !important;
        box-shadow: 
            0 12px 24px -2px rgba(79, 70, 229, 0.55),
            inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
    }

    .stButton > button:active {
        transform: translateY(3px) !important;
        border-bottom: 1px solid #312e81 !important;
        box-shadow: 
            0 2px 8px rgba(79, 70, 229, 0.3),
            inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    /* File Uploader 3D Styling */
    div[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.45) !important;
        border: 2px dashed rgba(99, 102, 241, 0.3) !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        box-shadow: 
            inset 0 2px 6px rgba(0, 0, 0, 0.3),
            0 1px 0 rgba(255, 255, 255, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: #818cf8 !important;
        background: rgba(99, 102, 241, 0.06) !important;
        box-shadow: 
            0 8px 24px -8px rgba(99, 102, 241, 0.2),
            inset 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }

    /* 3D Elevated Answer Box */
    .answer-card {
        background: linear-gradient(145deg, rgba(26, 36, 62, 0.75) 0%, rgba(13, 20, 37, 0.85) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-left: 5px solid #6366f1;
        border-radius: 16px;
        padding: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 
            0 16px 36px -10px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
    }

    .answer-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.9rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .answer-body {
        color: #f1f5f9;
        font-size: 1.02rem;
        line-height: 1.65;
        white-space: pre-wrap;
    }

    /* Source Links Cards */
    .source-chip {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.6rem 0.9rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: #cbd5e1;
        box-shadow: 
            0 4px 10px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.2s ease;
    }

    .source-chip:hover {
        background: rgba(30, 41, 69, 0.8);
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateX(4px);
    }

    .source-icon {
        color: #818cf8;
        font-size: 1rem;
    }

    /* File List Chips */
    .file-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 8px;
        padding: 0.35rem 0.75rem;
        margin: 0.25rem 0.35rem 0.25rem 0;
        font-size: 0.82rem;
        color: #e2e8f0;
    }

    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 2rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3D Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">⚡ AI-Powered Research Engine</div>
    <h1 class="hero-title">Researcher Research Assistant</h1>
    <p class="hero-sub">Deep synthesis of online articles & multi-format documents with verified retrieval-augmented intelligence.</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'docs_processed' not in st.session_state:
    st.session_state.docs_processed = False
if 'urls_processed' not in st.session_state:
    st.session_state.urls_processed = False

# Create tabs
tab1, tab2 = st.tabs(["🔗 Tab 1 - Web URLs", "📄 Tab 2 - Document Upload"])

# Tab 1: URL Processing
with tab1:
    st.markdown('<div class="section-title"><span class="icon">🔗</span> Links - Click Here</div>', unsafe_allow_html=True)
    
    url1 = st.text_input("URL 1", placeholder="https://example.com/research-article-1", key="url1")
    url2 = st.text_input("URL 2", placeholder="https://example.com/research-article-2", key="url2")
    url3 = st.text_input("URL 3", placeholder="https://example.com/research-article-3", key="url3")
    
    placeholder1 = st.empty()
    
    process_url_button = st.button("Process URLs", key="process_urls")
    if process_url_button:
        urls = [url for url in (url1, url2, url3) if url != '']
        if len(urls) == 0:
            placeholder1.error("You must provide at least one valid URL")
        else:
            try:
                for status in process_urls(urls):
                    placeholder1.text(status)
                placeholder1.success("URLs processed successfully!")
                st.session_state.urls_processed = True
                st.session_state.docs_processed = False  # Reset docs flag
            except RuntimeError as e:
                placeholder1.error(str(e))
    
    st.divider()
    
    st.markdown('<div class="section-title"><span class="icon">💡</span> Ask Questions to Your Topic</div>', unsafe_allow_html=True)
    query1 = st.text_input("Ask questions to your Topic", placeholder="e.g. Summarize the key findings across these sources...", key="query1")
    if query1:
        try:
            with st.spinner("Analyzing knowledge base & generating answer..."):
                answer, sources = generate_answer(query1)
            
            # 3D Answer Display
            st.markdown(f"""
            <div class="answer-card">
                <div class="answer-tag">✨ Synthesized Answer</div>
                <div class="answer-body">{answer}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if sources:
                st.markdown('<div class="section-title" style="font-size: 1rem;"><span class="icon" style="width:26px; height:26px;">📌</span> Source References:</div>', unsafe_allow_html=True)
                for source in sources.split("\n"):
                    if source.strip():
                        st.markdown(f"""
                        <div class="source-chip">
                            <span class="source-icon">🔗</span>
                            <span>{source}</span>
                        </div>
                        """, unsafe_allow_html=True)
        except RuntimeError as e:
            st.error("You must process URLs first")

# Tab 2: Document Upload
with tab2:
    st.markdown('<div class="section-title"><span class="icon">📁</span> Upload your PDFs (or) DOC, etc</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    placeholder2 = st.empty()
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) ready for ingestion:**")
        files_html = "".join([f'<span class="file-chip">📄 {f.name}</span>' for f in uploaded_files])
        st.markdown(files_html, unsafe_allow_html=True)
        st.write("")
    
    process_docs_button = st.button("Process Documents", key="process_docs")
    if process_docs_button:
        if not uploaded_files:
            placeholder2.error("Please upload at least one document")
        else:
            status_messages = []
            status_container = placeholder2.container()
            success = False
            error_occurred = False
            
            try:
                for status in process_documents(uploaded_files):
                    status_messages.append(status)
                    status_container.text(status)
                    if "Done!" in status or "chunks to vector database" in status:
                        success = True
                    if "❌" in status or "Error" in status or "failed" in status.lower():
                        error_occurred = True
            except RuntimeError as e:
                error_occurred = True
                status_messages.append(str(e))
                status_container.error(str(e))
            
            # Display final status
            if success and not error_occurred:
                placeholder2.success("✅ Documents processed successfully! You can now ask questions.")
                st.session_state.docs_processed = True
                st.session_state.urls_processed = False  # Reset URLs flag
            else:
                # Show all error messages
                error_text = "\n".join([msg for msg in status_messages if "❌" in msg or "Error" in msg or "failed" in msg.lower() or "No documents" in msg or "GROQ_API_KEY" in msg])
                if error_text:
                    placeholder2.error(f"❌ Processing failed:\n\n{error_text}")
                else:
                    placeholder2.error("❌ Document processing failed. Please check the status messages above.")
    
    st.divider()
    
    st.markdown('<div class="section-title"><span class="icon">💬</span> Ask Questions to Your Documents</div>', unsafe_allow_html=True)
    query2 = st.text_input("Type Question", placeholder="e.g. What are the key conclusions in chapter 3?", key="query2")
    if query2:
        try:
            with st.spinner("Searching documents and generating answer..."):
                answer, sources = generate_answer(query2)
            
            # 3D Answer Display
            st.markdown(f"""
            <div class="answer-card">
                <div class="answer-tag">✨ Synthesized Answer</div>
                <div class="answer-body">{answer}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if sources:
                st.markdown('<div class="section-title" style="font-size: 1rem;"><span class="icon" style="width:26px; height:26px;">📌</span> Source References:</div>', unsafe_allow_html=True)
                for source in sources.split("\n"):
                    if source.strip():
                        st.markdown(f"""
                        <div class="source-chip">
                            <span class="source-icon">📄</span>
                            <span>{source}</span>
                        </div>
                        """, unsafe_allow_html=True)
        except RuntimeError as e:
            if not st.session_state.docs_processed:
                st.error("You must process documents first. Please upload and process documents before asking questions.")
            else:
                st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
