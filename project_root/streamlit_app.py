import streamlit as st
import os
import re
import sys

# Must be the first Streamlit command
st.set_page_config(
    page_title="Telecom AI Brand Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Determine the parent directory where the UI scripts are located
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

if current_dir not in sys.path:
    sys.path.append(current_dir)
from locales import t

LANGUAGES = ["English", "Español", "Français"]

# ── Initialise defaults ──────────────────────────────────────────────────────
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "theme" not in st.session_state:
    st.session_state["theme"] = "Dark Mode"

# ── SIDEBAR: Language + Navigation ──────────────────────────────────────────
with st.sidebar:
    # Language selector at the very top of sidebar
    st.markdown("##### 🌐 Language / Idioma / Langue")
    lang_idx = LANGUAGES.index(st.session_state["language"])
    selected_lang = st.selectbox(
        "Select Language",
        LANGUAGES,
        index=lang_idx,
        label_visibility="collapsed",
    )
    # Write back to session state immediately
    st.session_state["language"] = selected_lang
    lang = selected_lang

    st.markdown("---")

    st.markdown(f"""
    <div style="text-align:center;padding:.3rem 0 1rem">
        <div style="font-size:1.05rem;font-weight:600;margin-top:.3rem">
            {t("nav_title", lang)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_options = [t("nav_analyst", lang), t("nav_customer", lang), t("nav_rag", lang)]
    app_mode_translated = st.radio("", nav_options)

internal_modes = [
    "Telecom Brand Analyst Dashboard",
    "Customer User Interface",
    "RAG Document Management",
]
app_mode = internal_modes[nav_options.index(app_mode_translated)]

# ── Top bar: Theme toggle only ───────────────────────────────────────────────
col_space, col_toggle = st.columns([9, 1])
with col_toggle:
    is_light = st.toggle(
        t("theme_toggle", lang),
        value=(st.session_state["theme"] == "Light Mode"),
    )
    st.session_state["theme"] = "Light Mode" if is_light else "Dark Mode"

# ── Inject widget-label colour fix ──────────────────────────────────────────
text_color = "#111827" if st.session_state["theme"] == "Light Mode" else "#d8e8ff"
st.markdown(f"""
<style>
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {{
    color: {text_color} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Load & exec sub-module ───────────────────────────────────────────────────
if app_mode == "Customer User Interface":
    file_path = os.path.join(parent_dir, "customer_ui.py")
elif app_mode == "RAG Document Management":
    file_path = os.path.join(parent_dir, "rag_management.py")
else:
    file_path = os.path.join(parent_dir, "analyst_dashboard.py")

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove any st.set_page_config call to prevent DuplicateError
code = re.sub(r'st\.set_page_config\([^)]*\)', '', code, flags=re.DOTALL)

namespace = {
    '__name__': '__main__',
    '__file__': file_path,
}
exec(code, namespace)
