import streamlit as st
import requests
import os

# ─── Custom CSS ─────────────────────────────────────────────────────────────
theme = st.session_state.get("theme", "Dark Mode")
if theme == "Light Mode":
    css_vars = """
    :root {
        --bg-deep:     #f4f7f6;
        --bg-card:     #ffffff;
        --bg-input:    #f9fafb;
        --border:      #d1d5db;
        --border-glow: #2563eb;
        --accent-blue: #2563eb;
        --accent-cyan: #0891b2;
        --text-primary:#111827;
        --text-muted:  #4b5563;
        --radius:      14px;
    }
    """
else:
    css_vars = """
    :root {
        --bg-deep:     #080c14;
        --bg-card:     #0d1525;
        --bg-input:    #111d30;
        --border:      #1e3050;
        --border-glow: #0a84ff;
        --accent-blue: #0a84ff;
        --accent-cyan: #00d4ff;
        --text-primary:#e8f4ff;
        --text-muted:  #5a7a9a;
        --radius:      14px;
    }
    """

st.markdown("<style>@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');\n" + css_vars + """

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--bg-deep);
    color: var(--text-primary);
}

.stApp { background: var(--bg-deep); }
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; pointer-events: none; }
[data-testid="collapsedControl"] { pointer-events: auto; }
[data-testid="stToolbar"] { visibility: hidden !important; }

/* Override Streamlit Native Text Colors */
.stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown div,
[data-testid="stExpander"] p, [data-testid="stExpander"] span, [data-testid="stExpander"] summary, [data-testid="stExpander"] div,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div[data-baseweb="radio"] div,
[data-testid="stWidgetLabel"] p {
    color: var(--text-primary) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(10,132,255,.15), rgba(0,212,255,.1));
    border: 1px solid rgba(0,212,255,.3);
    color: var(--accent-cyan);
    font-family: 'JetBrains Mono', monospace;
    font-size: .7rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    padding: .4rem 1.1rem;
    border-radius: 100px;
    margin-bottom: 1.4rem;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0 0 .8rem;
    background: linear-gradient(135deg, #e8f4ff 0%, #00d4ff 60%, #0a84ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: .95rem;
    color: var(--text-muted);
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto 2.5rem;
    line-height: 1.6;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(10,132,255,.5), transparent);
}
.card-title {
    font-size: .75rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent-blue);
    margin-bottom: 1rem;
}

/* ── Button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0a84ff, #0060cc) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    letter-spacing: .03em;
    padding: .85rem 0 !important;
    cursor: pointer;
    transition: all .2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1a94ff, #0070dd) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(10,132,255,.35) !important;
}

/* ── Response Box ── */
.response-box {
    background: linear-gradient(135deg, rgba(10,132,255,.07), rgba(0,212,255,.04));
    border: 1px solid rgba(10,132,255,.3);
    border-radius: var(--radius);
    padding: 1.6rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─── UI Layout ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-badge">📚 Knowledge Base Management</div>
    <div class="hero-title">RAG Document Indexing</div>
    <div class="hero-sub">Upload policies, guides, and documentation to be ingested by the AI's Retrieval-Augmented Generation system.</div>
</div>
""", unsafe_allow_html=True)


tab_upload, tab_audit = st.tabs(["🚀 Upload & Index", "📋 Document Audit"])

with tab_upload:
    # ── Upload Section
    st.markdown('<div class="card"><div class="card-title">✦ Upload New Document</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Select PDF or TXT File", type=["pdf", "txt"], help="Supported formats: PDF, TXT")

    if st.button("🚀 Upload & Index Document"):
        if uploaded_file is not None:
            with st.spinner("Processing and indexing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post("http://127.0.0.1:8000/upload", files=files)
                    
                    if res.status_code == 200:
                        st.success(f"Successfully uploaded and indexed: {uploaded_file.name}")
                    else:
                        st.error(f"Failed to upload. Status {res.status_code}: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Failed to connect to the backend API. Is FastAPI running on port 8000?")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please select a file to upload.")

    st.markdown('</div>', unsafe_allow_html=True)

with tab_audit:
    st.markdown('<div class="card"><div class="card-title">✦ Active Policy Documents</div>', unsafe_allow_html=True)
    
    def delete_doc(filename):
        try:
            res = requests.delete(f"http://127.0.0.1:8000/documents/{filename}")
            if res.status_code == 200:
                st.toast(f"✅ Deleted {filename} and rebuilt index!")
            else:
                st.error(f"Failed to delete {filename}: {res.text}")
        except Exception as e:
            st.error(f"API Error: {str(e)}")

    try:
        res = requests.get("http://127.0.0.1:8000/documents")
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            if not docs:
                st.info("No custom documents uploaded yet. Using default telecom policies.")
            else:
                for doc in docs:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:1rem; border:1px solid var(--border); border-radius:8px; margin-bottom:0.4rem; background:var(--bg-hover);">
                        <div style="display:flex; flex-direction:column;">
                            <span style="font-weight:600; color:var(--text-primary); margin-bottom:0.3rem;">📄 {doc['filename']}</span>
                            <span style="font-size:0.75rem; color:var(--text-muted); font-family:'JetBrains Mono', monospace;">{doc['size_kb']} KB</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button("🗑️ Delete Document", key=f"del_{doc['filename']}", on_click=delete_doc, args=(doc['filename'],), use_container_width=True)
                    st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)
        else:
            st.error("Failed to load documents.")
    except Exception:
        st.warning("Backend API is unreachable. Cannot load documents.")
        
    st.markdown('</div>', unsafe_allow_html=True)


# ── Query Test Section
st.markdown('<div class="card"><div class="card-title">✦ Test RAG Retrieval</div>', unsafe_allow_html=True)

test_query = st.text_input("Test query to the RAG system", placeholder="e.g. What is the SLA for network outages?")

if st.button("🔍 Query System"):
    if test_query:
        with st.spinner("Retrieving from knowledge base..."):
            try:
                payload = {"question": test_query, "username": "admin_test"}
                res = requests.post("http://127.0.0.1:8000/ask", json=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    st.markdown(f"""
                    <div class="response-box">
                        <div style="font-size:0.75rem; color:var(--accent-cyan); margin-bottom:0.8rem; font-family:'JetBrains Mono', monospace;">AI GENERATED RESPONSE</div>
                        <div style="font-size:0.95rem; line-height:1.6; color:var(--text-primary);">{data.get('answer', 'No answer')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("View Retrieved Context & Metadata"):
                        st.write(f"**Confidence Score:** {data.get('confidence', 0)}")
                        st.markdown("**Context Used:**")
                        st.info(data.get('context', 'No context retrieved'))
                else:
                    st.error(f"Failed to query. Status {res.status_code}: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend API. Is FastAPI running on port 8000?")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a question to test.")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;margin-top:3rem;color:var(--text-muted);font-size:.75rem;font-family:'JetBrains Mono',monospace;">
    TELECOMAI BRAND INTELLIGENCE SYSTEM &nbsp;·&nbsp; RAG INDEXING PORTAL
</div>
""", unsafe_allow_html=True)
