import streamlit as st
import random
import time
import json
import os
import requests
from datetime import datetime

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
from locales import t
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
except ImportError:
    Groq = None

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TelecomAI · Customer Portal",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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
        --accent-teal: #0d9488;
        --text-primary:#111827;
        --text-muted:  #4b5563;
        --pos-color:   #059669;
        --neu-color:   #d97706;
        --neg-color:   #dc2626;
        --mix-color:   #7c3aed;
        --radius:      14px;
        --bg-hover:    #f3f4f6;
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
        --accent-teal: #00e5c3;
        --text-primary:#e8f4ff;
        --text-muted:  #5a7a9a;
        --pos-color:   #00e5c3;
        --neu-color:   #f5a623;
        --neg-color:   #ff453a;
        --mix-color:   #9b7dff;
        --radius:      14px;
        --bg-hover:    #172336;
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

/* ── Hide Streamlit chrome ── */
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
.block-container { padding: 2rem 1.5rem 4rem; max-width: 780px; }

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

/* ── Textarea ── */
.stTextArea textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: .92rem !important;
    resize: none !important;
    padding: 1rem !important;
    transition: border-color .25s;
}
.stTextArea textarea:focus {
    border-color: var(--border-glow) !important;
    box-shadow: 0 0 0 3px rgba(10,132,255,.12) !important;
}

/* ── Select boxes ── */
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
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
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1a94ff, #0070dd) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(10,132,255,.35) !important;
}
.stButton > button:active { transform: translateY(0); }

/* ── Sentiment Pills ── */
.sentiment-row {
    display: flex;
    gap: .8rem;
    margin-bottom: 1.2rem;
    flex-wrap: wrap;
}
.pill {
    display: flex; align-items: center; gap: .5rem;
    padding: .5rem 1.1rem;
    border-radius: 100px;
    font-size: .82rem;
    font-weight: 600;
    border: 1px solid;
}
.pill-pos { background: rgba(0,229,195,.1); border-color: rgba(0,229,195,.35); color: var(--pos-color); }
.pill-neu { background: rgba(245,166,35,.1);  border-color: rgba(245,166,35,.35);  color: var(--neu-color); }
.pill-mix { background: rgba(155,125,255,.1); border-color: rgba(155,125,255,.35); color: var(--mix-color); }
.pill-neg { background: rgba(255,69,58,.1);  border-color: rgba(255,69,58,.35);  color: var(--neg-color); }
.pill-active-pos { background: rgba(0,229,195,.2); border-color: var(--pos-color); box-shadow: 0 0 12px rgba(0,229,195,.25); }
.pill-active-neu { background: rgba(245,166,35,.2); border-color: var(--neu-color); box-shadow: 0 0 12px rgba(245,166,35,.25); }
.pill-active-mix { background: rgba(155,125,255,.2); border-color: var(--mix-color); box-shadow: 0 0 12px rgba(155,125,255,.25); }
.pill-active-neg { background: rgba(255,69,58,.2); border-color: var(--neg-color); box-shadow: 0 0 12px rgba(255,69,58,.25); }

/* ── Response Box ── */
.response-box {
    background: linear-gradient(135deg, rgba(10,132,255,.07), rgba(0,212,255,.04));
    border: 1px solid rgba(10,132,255,.3);
    border-radius: var(--radius);
    padding: 1.6rem;
    position: relative;
}
.response-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #0a84ff, #00d4ff, #00e5c3);
    border-radius: var(--radius) var(--radius) 0 0;
}
.response-label {
    font-size: .7rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--accent-cyan);
    margin-bottom: .9rem;
}
.response-text {
    font-size: .95rem;
    line-height: 1.7;
    color: var(--text-primary);
}

/* ── Meta chips ── */
.meta-row {
    display: flex; gap: .7rem; flex-wrap: wrap; margin-top: 1.1rem;
}
.meta-chip {
    display: flex; align-items: center; gap: .4rem;
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 8px;
    padding: .38rem .8rem;
    font-size: .78rem;
    color: var(--text-muted);
}
.meta-chip span { color: var(--text-primary); font-weight: 500; }

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}

/* ── RAG section ── */
.rag-item {
    display: flex; align-items: flex-start; gap: .75rem;
    padding: .9rem;
    background: rgba(255,255,255,.03);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: .6rem;
}
.rag-icon {
    font-size: 1.1rem; margin-top: .05rem; flex-shrink: 0;
}
.rag-content { flex: 1; }
.rag-doc { font-size: .82rem; font-weight: 600; color: var(--accent-blue); margin-bottom: .2rem; }
.rag-excerpt { font-size: .78rem; color: var(--text-muted); line-height: 1.5; }

/* ── Confidence bar ── */
.conf-bar-bg {
    background: rgba(255,255,255,.07);
    border-radius: 100px;
    height: 6px;
    margin-top: .5rem;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #0a84ff, #00d4ff);
    transition: width 1s ease;
}

/* ── Label override ── */
label, .stSelectbox label, .stTextArea label {
    color: var(--text-muted) !important;
    font-size: .8rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
}

/* ── Tabs Style ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
}
.stTabs [data-baseweb="tab"] {
    height: 3rem;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    padding: 0 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Sample Data & Simulation ────────────────────────────────────────────────
CATEGORIES = [
    "Network Connectivity", "Billing & Payments", "Data Services",
    "Roaming & International", "Customer Support", "Device & SIM",
    "Plan & Subscription", "Voice & Calls",
]

RAG_DOCS = {
    "Network Connectivity": [
        ("Network Service Policy v3.2", "Planned maintenance windows are communicated 48h in advance. Emergency outages are resolved within 4 hours per SLA."),
        ("Troubleshooting Guide — Connectivity", "Users experiencing signal drops should toggle Airplane mode, check APN settings, or contact support for network diagnostics."),
    ],
    "Billing & Payments": [
        ("Billing Policy 2024", "Invoices are generated on the 1st of each month. Disputed charges must be raised within 30 days of the billing date."),
        ("Refund & Credit Guidelines", "Approved refunds are processed within 5–7 business days back to the original payment method."),
    ],
    "Data Services": [
        ("Fair Usage Policy", "After exhausting the high-speed data quota, speeds are throttled to 512 kbps until the next billing cycle."),
        ("Data Plan Terms", "Data rollover applies only to monthly plans above 20 GB. Rollover data expires after 30 days."),
    ],
    "Plan & Subscription": [
        ("Plan Change Policy", "Upgrades take effect immediately; downgrades apply from the next billing cycle. No cancellation fees apply."),
        ("Activation SLA", "New SIM activation requests are processed within 24–72 hours. Delays may occur during peak periods (up to 7 days)."),
    ],
}

@st.cache_resource
def load_sentiment_model():
    from transformers import pipeline
    # Load DistilBERT explicitly fine-tuned for sentiment analysis
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def get_rag_docs(category: str):
    return RAG_DOCS.get(category, [("General Support Policy", "For any other inquiries, our customer support team is available 24/7.")])

def analyze_feedback(text: str):
    """Uses DistilBERT for baseline, and Groq LLM for reasoning, category, and final sentiment."""
    # 1. DistilBERT Baseline
    try:
        classifier = load_sentiment_model()
        bert_result = classifier(text)[0]
        bert_label = bert_result['label'].capitalize()
        bert_score = bert_result['score']
    except Exception:
        bert_label = "Neutral"
        bert_score = 0.5

    # 2. Groq LLM Reasoning & Refinement
    from dotenv import load_dotenv
    load_dotenv(override=True)
    if not Groq or not os.environ.get("GROQ_API_KEY"):
        return "Neutral", 0.5, "Customer Support", "Groq API missing. Mock response."
        
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    prompt = f"""
    You are an expert Telecom Data Scientist for ZENDS Communications. Classify the aspect-based sentiment of the target customer ticket and identify its category.
    
    RULES:
    - Sentiment must be exactly one of: [Positive, Negative, Neutral, Mixed]
    - Only evaluate sentiment directed at ZENDS Communications. Ignore anger directed at external factors (pets, weather, user error). Do not fall for the "Conjunction Trap" (just because a sentence contains "but" or "however" does not make it "Mixed").
    - Category must be exactly one of: ["Network Connectivity", "Billing & Payments", "Data Services", "Roaming & International", "Customer Support", "Device & SIM", "Plan & Subscription", "Voice & Calls"]

    === EXAMPLES ===
    
    Ticket: "I love the new phone, but my dog just chewed up the charging cable."
    Reasoning: The user is happy with the phone (Positive toward ZENDS). The negative event is the dog chewing the cable, which is external. Therefore, the sentiment toward ZENDS is Positive.

    Ticket: "Your internet speeds are blazing fast, but your customer service agent was incredibly rude to me."
    Reasoning: The user praises the speed (Positive toward ZENDS) but complains about the agent (Negative toward ZENDS). Since both are our responsibility, the sentiment is Mixed.

    Ticket: "I want to pay my bill."
    Reasoning: The user is stating an intent. There is no strong emotion or opinion expressed. (Sentiment: Neutral)

    === NOW EVALUATE THE TARGET TICKET ===

    Ticket: "{text}"
    
    The baseline model (DistilBERT) classified it as {bert_label} (Confidence: {bert_score:.2f}).
    
    Please provide a refined analysis based on the rules. 
    Return your response strictly in the following JSON format:
    {{
        "sentiment": "Positive" | "Neutral" | "Negative" | "Mixed",
        "category": "<Category>",
        "confidence": <float between 0 and 1>,
        "reasoning": "<short reasoning for this classification based on the rules>"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a highly analytical AI assistant for a telecom brand. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("sentiment", "Neutral"), result.get("confidence", 0.5), result.get("category", "Customer Support"), result.get("reasoning", "")
    except Exception as e:
        return "Neutral", 0.5, "Customer Support", f"Failed to analyze: {str(e)}"

def generate_response(sentiment: str, category: str, feedback: str, reasoning: str, rag_docs: list, lang="English") -> str:
    """Returns a static response based on sentiment."""
    if sentiment in ["Positive", "Neutral"]:
        if lang == "Español": return "Gracias por su comentario."
        if lang == "Français": return "Merci pour votre commentaire."
        return "Thank you for your feedback."
    else:
        if lang == "Español": return "Gracias por su comentario. Revisaremos su problema y nos pondremos en contacto con usted en breve."
        if lang == "Français": return "Merci pour votre commentaire. Nous examinerons votre problème et vous répondrons sous peu."
        return "Thank you for your feedback. We will review your concern and get back to you shortly."


# ─── UI Layout ───────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-badge">📡 AI-Powered Customer Portal</div>
    <div class="hero-title">How can we help you today?</div>
    <div class="hero-sub">Share your experience and our AI system will instantly analyze your feedback, identify your concern, and connect you with the right solutions.</div>
</div>
""", unsafe_allow_html=True)


tab_customer, tab_rag = st.tabs(["💬 Customer Portal", "⚙️ RAG Document Management"])

with tab_customer:
    # ── FAQ Section
    st.markdown('<div class="card"><div class="card-title">✦ Frequently Asked Questions</div>', unsafe_allow_html=True)
    
    faq_category = st.selectbox("Select FAQ Category", [
        "Mobile Network", 
        "Broadband Service", 
        "Billing & Payments", 
        "Customer Support", 
        "Mobile App Issues", 
        "Service Activation"
    ])
    
    if faq_category == "Mobile Network":
        st.markdown("**What my Mobile network services include:**\n- 5G mobile connectivity\n- Voice calling\n- SMS messaging\n- International roaming\n- SIM and eSIM provisioning\n- Data add-on packages")
        with st.expander("Q1: Why is my mobile network signal weak?"):
            st.write("**Possible causes:** low coverage area, indoor obstruction, or temporary network maintenance.")
            st.write("**Solution:** Move to an open area or restart the device. If the issue persists, contact support.")
        with st.expander("Q2: Why is my mobile data not working?"):
            st.write("**Possible causes:** Data pack expired, APN configuration issues, or temporary network outage.")
            st.write("**Solution:** Check mobile data settings or restart your device.")
        with st.expander("Q3: Why are my calls dropping frequently?"):
            st.write("**Possible causes:** Network congestion, weak signal, or device compatibility issues.")
            st.write("**Solution:** Switch to 4G/5G mode or move to a stronger signal location.")
    
    elif faq_category == "Broadband Service":
        st.markdown("**ZENDS provides high-speed fiber broadband services including:**\n- ZENDFiber Home 100 Mbps\n- ZENDFiber Home 300 Mbps\n- ZENDFiber Home 1 Gbps")
        with st.expander("Q1: Why is my broadband internet slow?"):
            st.write("**Possible causes:** Network congestion, router issues, or high number of connected devices.")
            st.write("**Solution:** Restart the router and check connected devices.")
        with st.expander("Q2: My internet is completely down. What should I do?"):
            st.write("**Possible causes:** Fiber cable damage, service outage, or router malfunction.")
            st.write("**Solution:** Restart modem/router. If the issue continues, report it to support.")
    
    elif faq_category == "Billing & Payments":
        st.markdown("**ZENDS follows monthly advance billing.**")
        with st.expander("Q1: Why is my bill higher than expected?"):
            st.write("**Possible reasons:** Extra data usage, international roaming charges, or add-on services.")
        with st.expander("Q2: When is my payment due?"):
            st.write("Bills must be paid within 7 days of invoice generation. Late payment may lead to temporary service suspension.")
        with st.expander("Q3: Can I get a refund?"):
            st.write("**Refund policy:** Full refund within 7 days if usage is below 10%. Cloud services are non-refundable after activation.")
    
    elif faq_category == "Customer Support":
        st.markdown("**ZENDS provides 24×7 support services.**")
        with st.expander("Q1: How can I contact customer support?"):
            st.markdown("Customers can reach support via:\n- Mobile App\n- Website chat\n- Phone support\n- Email support")
        with st.expander("Q2: What are the support levels?"):
            st.markdown("Support tiers include:\n- Standard Support\n- Priority Support\n- Enterprise Dedicated Support")
    
    elif faq_category == "Mobile App Issues":
        st.markdown("**Customers use the ZENDS mobile app for:**\n- Bill payments\n- Plan upgrades\n- Data usage monitoring\n- Support requests")
        with st.expander("Issue 1: App login failure"):
            st.write("**Solution:** Reset password, clear app cache, update the application.")
        with st.expander("Issue 2: Payment failure in the app"):
            st.write("**Solution:** Verify payment gateway, check internet connectivity, retry transaction.")
    
    elif faq_category == "Service Activation":
        st.markdown("**Common Issues**")
        with st.expander("New SIM activation delay"):
            st.write("Activation may take up to 24 hours.")
        with st.expander("Broadband installation delay"):
            st.write("Installation may take 3–5 business days.")
        with st.expander("eSIM activation failure"):
            st.write("Restart device and rescan QR code.")
        with st.expander("Mobile plan upgrade delay"):
            st.write("Changes may reflect within 2 hours.")
        with st.expander("Broadband plan upgrade delay"):
            st.write("Upgrade processed within 24 hours.")
        with st.expander("SIM replacement activation delay"):
            st.write("Replacement activation takes 4–6 hours.")
        with st.expander("International roaming activation delay"):
            st.write("Roaming services may take 1 hour to activate.")
        with st.expander("Add-on data pack activation delay"):
            st.write("Data pack activates instantly or within 10 minutes.")
        with st.expander("Payment verification delay"):
            st.write("Payments may take up to 30 minutes to reflect.")
        with st.expander("New customer account verification delay"):
            st.write("Identity verification may take up to 24 hours.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ── Input Card
    st.markdown('<div class="card"><div class="card-title">✦ Submit Your Feedback</div>', unsafe_allow_html=True)
    
    lang = st.session_state.get("language", "English")
    
    feedback_text = st.text_area(
        "Your Message" if lang == "English" else ("Su Mensaje" if lang == "Español" else "Votre Message"),
        placeholder=t("feedback_placeholder", lang),
        height=130,
        key="feedback_input",
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        account_type = st.selectbox("Account Type", ["Prepaid", "Postpaid", "Business", "Enterprise"])
    with col2:
        department = st.selectbox("Department", [
            "Mobile Network", "Broadband Service", "Billing & Payments", 
            "Customer Support", "Mobile App Issues", "Service Activation", "Other"
        ])
    with col3:
        priority = st.selectbox("Priority Level", ["Normal", "Urgent", "Critical"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ── Submit
    def mark_resolved(t_id):
        feed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_root", "data", "live_feedback.json")
        try:
            if os.path.exists(feed_path):
                with open(feed_path, "r", encoding="utf-8") as f: feed_data = json.load(f)
                for item in feed_data:
                    if item.get("id") == t_id:
                        item["status"] = "Resolved"
                        break
                with open(feed_path, "w", encoding="utf-8") as f: json.dump(feed_data, f, indent=2)
                st.toast("✅ Ticket marked as resolved!")
        except Exception: pass
    
    submitted = st.button(t("btn_analyze", lang), use_container_width=True)
    
    # ── Processing & Results
    if submitted and feedback_text.strip():
    
        with st.spinner(""):
            progress = st.progress(0, text="Initializing NLP pipeline…")
            
            progress.progress(25, text="Running DistilBERT & Groq LLM reasoning…")
            sentiment, confidence, category, reasoning = analyze_feedback(feedback_text)
            
            progress.progress(75, text="Retrieving relevant policies via RAG…")
            rag_docs  = get_rag_docs(category)
            
            progress.progress(100, text="Generating AI response via Groq…")
            ai_reply  = generate_response(sentiment, category, feedback_text, reasoning, rag_docs, lang)
            
            time.sleep(0.3)
            progress.empty()
    
            ticket_id = f"TCK-{random.randint(100000,999999)}" if sentiment in ["Negative", "Mixed"] else None
            
            # Wire up Live Feed for Analyst Dashboard
            try:
                data_record = {
                    "id": ticket_id or f"FB-{random.randint(10000,99999)}",
                    "timestamp": datetime.now().isoformat(),
                    "category": category,
                    "sentiment": sentiment,
                    "feedback": feedback_text,
                    "confidence": int(confidence*100),
                    "status": "Pending" if ticket_id else "No Action"
                }
                feed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_root", "data", "live_feedback.json")
                if os.path.exists(feed_path):
                    with open(feed_path, "r", encoding="utf-8") as f:
                        feed_data = json.load(f)
                else:
                    feed_data = []
                feed_data.insert(0, data_record)
                with open(feed_path, "w", encoding="utf-8") as f:
                    json.dump(feed_data[:50], f, indent=2)
            except Exception as e:
                pass
    
        # Sentiment result
        pill_cls = {"Positive": "pill-pos pill-active-pos", "Neutral": "pill-neu pill-active-neu", "Mixed": "pill-mix pill-active-mix", "Negative": "pill-neg pill-active-neg"}[sentiment]
        icon     = {"Positive": "●", "Neutral": "◐", "Mixed": "◑", "Negative": "●"}[sentiment]
    
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✦ Analysis Results</div>
            <div class="sentiment-row">
                <div class="pill {pill_cls}">{icon} {sentiment} Sentiment</div>
                <div class="pill" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.15);color:#8aaccc;">
                    📂 {category}
                </div>
                <div class="pill" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.15);color:#8aaccc;">
                    ⚡ {priority} Priority
                </div>
            </div>
            <div style="color:var(--text-muted);font-size:.8rem;margin-bottom:.4rem;">Model Confidence</div>
            <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{int(confidence*100)}%"></div></div>
            <div style="color:var(--text-muted);font-size:.75rem;margin-top:.4rem;text-align:right;">{int(confidence*100)}%</div>
        </div>
        """, unsafe_allow_html=True)
    
        # RAG Documents
        st.markdown('<div class="card"><div class="card-title">✦ Retrieved Policy Documents (RAG)</div>', unsafe_allow_html=True)
        for doc_name, excerpt in rag_docs:
            st.markdown(f"""
            <div class="rag-item">
                <div class="rag-icon">📄</div>
                <div class="rag-content">
                    <div class="rag-doc">{doc_name}</div>
                    <div class="rag-excerpt">{excerpt}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
        ticket_html = f'<div class="meta-chip">Ticket <span>#{ticket_id}</span></div>' if ticket_id else ""
    
        # AI Response
        html_content = f"""
        <div class="card">
            <div class="card-title">{t("ai_response_title", lang)}</div>
            <div class="response-box">
                <div class="response-label">{t("ai_assistant", lang)}</div>
                <div class="response-text">{ai_reply}</div>
                <div class="meta-row">
                    <div class="meta-chip">Account <span>{account_type}</span></div>
                    <div class="meta-chip">Department <span>{department}</span></div>
                    <div class="meta-chip">Category <span>{category}</span></div>{ticket_html}
                </div>
                <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(0,0,0,0.15); border-radius: 8px; font-size: 0.8rem; border-left: 3px solid var(--accent-blue);">
                    <strong style="color:var(--text-muted); font-family: 'JetBrains Mono', monospace;">GROQ REASONING:</strong> {reasoning}
                </div>
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
    
        # Actions
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button(t("btn_callback", lang))
        with c2:
            st.button(t("btn_email", lang))
        with c3:
            if ticket_id:
                st.button(t("btn_resolved", lang), on_click=mark_resolved, args=(ticket_id,))
            else:
                st.button(t("btn_resolved", lang))
    
    elif submitted:
        st.warning("Please enter your feedback before submitting.")
    
    # Footer
    st.markdown("""
    <div style="text-align:center;margin-top:3rem;color:var(--text-muted);font-size:.75rem;font-family:'JetBrains Mono',monospace;">
        TELECOMAI BRAND INTELLIGENCE SYSTEM &nbsp;·&nbsp; CUSTOMER PORTAL v2.1
    </div>
    """, unsafe_allow_html=True)

with tab_rag:
    # ── Upload Section
    st.markdown('<div class="card" style="margin-top: 1rem;"><div class="card-title">✦ Upload New Document</div>', unsafe_allow_html=True)

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

    # ── Audit Section
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
                        <div class="response-box" style="margin-top: 1rem;">
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
