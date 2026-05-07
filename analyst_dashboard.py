import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
import time
import json
import os
from datetime import datetime, timedelta

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TelecomAI · Analyst Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
theme = st.session_state.get("theme", "Dark Mode")
if theme == "Light Mode":
    css_vars = """
    :root {
        --bg:         #f0f2f5;
        --bg-panel:   #ffffff;
        --bg-card:    #ffffff;
        --bg-hover:   #e4e6eb;
        --border:     #d1d5db;
        --border-hi:  #9ca3af;
        --acc-blue:   #005bb5;
        --acc-green:  #009966;
        --acc-amber:  #d97706;
        --acc-red:    #dc2626;
        --acc-purple: #7c3aed;
        --txt-1:      #111827;
        --txt-2:      #4b5563;
        --txt-3:      #6b7280;
        --pos:        #009966;
        --neu:        #d97706;
        --neg:        #dc2626;
    }
    """
    PLOT_BG   = "rgba(0,0,0,0)"
    GRID_CLR  = "rgba(209,213,219,0.8)"
    FONT_CLR  = "#4b5563"
else:
    css_vars = """
    :root {
        --bg:         #07090f;
        --bg-panel:   #0c1018;
        --bg-card:    #111520;
        --bg-hover:   #161b28;
        --border:     #1c2535;
        --border-hi:  #2a3a55;
        --acc-blue:   #4d9fff;
        --acc-green:  #2dd4a0;
        --acc-amber:  #f5c842;
        --acc-red:    #ff5f5f;
        --acc-purple: #9b7dff;
        --txt-1:      #d8e8ff;
        --txt-2:      #6a88aa;
        --txt-3:      #3a5070;
        --pos:        #2dd4a0;
        --neu:        #f5c842;
        --neg:        #ff5f5f;
    }
    """
    PLOT_BG   = "rgba(0,0,0,0)"
    GRID_CLR  = "rgba(28,37,53,0.8)"
    FONT_CLR  = "#6a88aa"

st.markdown("<style>@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');\n" + css_vars + """

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: var(--bg);
    color: var(--txt-1);
}
.stApp { background: var(--bg); }
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; pointer-events: none; }
[data-testid="collapsedControl"] { pointer-events: auto; }
[data-testid="stToolbar"] { visibility: hidden !important; }

/* Override Streamlit Native Text Colors */
.stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown div,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div[data-baseweb="radio"] div,
[data-testid="stWidgetLabel"] p {
    color: var(--txt-1) !important;
}
[data-testid="stMetricValue"] {
    color: var(--txt-1) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 1rem;
}
section[data-testid="stSidebar"] .block-container { padding: 1rem; }

/* ── Main layout ── */
.block-container { padding: 1.5rem 2rem 3rem; }

/* ── Top bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.5rem;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.topbar-left { display: flex; align-items: center; gap: 1rem; }
.topbar-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #4d9fff, #2dd4a0);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.topbar-title { font-size: 1rem; font-weight: 600; color: var(--txt-1); }
.topbar-sub   { font-size: .73rem; color: var(--txt-2); margin-top: .1rem; }
.live-dot {
    display: flex; align-items: center; gap: .5rem;
    font-size: .75rem; color: var(--acc-green);
    font-family: 'IBM Plex Mono', monospace;
}
.dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--acc-green);
    box-shadow: 0 0 6px var(--acc-green);
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ── KPI Cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
}
.kpi:hover { border-color: var(--border-hi); }
.kpi::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.kpi-blue::after  { background: linear-gradient(90deg,#4d9fff,#9b7dff); }
.kpi-green::after { background: linear-gradient(90deg,#2dd4a0,#4d9fff); }
.kpi-amber::after { background: linear-gradient(90deg,#f5c842,#f59f42); }
.kpi-red::after   { background: linear-gradient(90deg,#ff5f5f,#ff9f5f); }

.kpi-label { font-size: .7rem; font-family:'IBM Plex Mono',monospace; letter-spacing:.1em; text-transform:uppercase; color:var(--txt-2); margin-bottom:.6rem; }
.kpi-value { font-size: 2rem; font-weight: 600; line-height:1; margin-bottom:.4rem; }
.kpi-delta { font-size: .75rem; color: var(--txt-2); }
.delta-pos { color: var(--pos); }
.delta-neg { color: var(--neg); }

/* ── Section headers ── */
.sec-head {
    font-size: .7rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--txt-2);
    margin-bottom: .9rem;
    display: flex; align-items: center; gap: .6rem;
}
.sec-head::after { content:''; flex:1; height:1px; background:var(--border); }

/* ── Chart panels ── */
.panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem;
    height: 100%;
}

/* ── Feed items ── */
.feed-item {
    display: flex; align-items: flex-start; gap: .9rem;
    padding: .85rem 0;
    border-bottom: 1px solid var(--border);
}
.feed-item:last-child { border-bottom: none; }
.feed-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; margin-top:.35rem; }
.feed-text { font-size:.82rem; color:var(--txt-1); line-height:1.5; }
.feed-meta { font-size:.7rem; color:var(--txt-2); margin-top:.2rem; font-family:'IBM Plex Mono',monospace; }

/* ── Recommendation card ── */
.rec-card {
    display:flex; gap:1rem;
    background: var(--bg-hover);
    border: 1px solid var(--border);
    border-left: 3px solid var(--acc-blue);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-bottom: .7rem;
}
.rec-icon { font-size:1.2rem; flex-shrink:0; }
.rec-title { font-size:.82rem; font-weight:600; color:var(--txt-1); margin-bottom:.25rem; }
.rec-body  { font-size:.76rem; color:var(--txt-2); line-height:1.5; }
.tag {
    display:inline-block;
    background:rgba(77,159,255,.15);
    border:1px solid rgba(77,159,255,.3);
    color:var(--acc-blue);
    font-size:.65rem;
    font-family:'IBM Plex Mono',monospace;
    padding:.2rem .55rem;
    border-radius:6px;
    margin-top:.4rem;
}

/* ── Plotly override ── */
.js-plotly-plot { border-radius: 10px; }

/* ── Selectbox / filter ── */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--txt-1) !important;
}
.stSlider > div { color: var(--txt-1) !important; }

label { color: var(--txt-2) !important; font-size:.75rem !important; font-family:'IBM Plex Mono',monospace !important; letter-spacing:.07em !important; }

/* ── Button ── */
.stButton>button {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border-hi) !important;
    color: var(--txt-1) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: .82rem !important;
}
.stButton>button:hover {
    border-color: var(--acc-blue) !important;
    color: var(--acc-blue) !important;
}

/* ── Tab ── */
.stTabs [data-baseweb="tab-list"] { background: var(--bg-card); border-radius: 10px; padding: .2rem; border:1px solid var(--border); }
.stTabs [data-baseweb="tab"] { color: var(--txt-2) !important; border-radius: 8px !important; }
.stTabs [aria-selected="true"] { background: var(--bg-hover) !important; color: var(--txt-1) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Synthetic Data ──────────────────────────────────────────────────────────
random.seed(42)

CATEGORIES = [
    "Network Connectivity", "Billing & Payments", "Data Services",
    "Roaming & International", "Customer Support", "Device & SIM",
    "Plan & Subscription", "Voice & Calls",
]

SENTIMENTS = ["Positive", "Neutral", "Mixed", "Negative"]
SENT_WEIGHTS = [0.28, 0.22, 0.10, 0.40]

SAMPLE_FEEDBACK = [
    ("Network Connectivity", "Negative", "Signal keeps dropping in my area for 3 days straight."),
    ("Billing & Payments",   "Negative", "Overcharged twice this month. No explanation given."),
    ("Data Services",        "Neutral",  "Data speed is okay but not what I expected for 5G."),
    ("Customer Support",     "Positive", "Agent resolved my issue quickly. Very satisfied!"),
    ("Plan & Subscription",  "Mixed", "The new plan is affordable, but the activation process was highly frustrating."),
    ("Plan & Subscription",  "Negative", "Tried to upgrade plan online but portal kept crashing."),
    ("Voice & Calls",        "Negative", "Calls dropping in the middle of every conversation."),
    ("Device & SIM",         "Neutral",  "SIM replacement took longer than expected but done now."),
    ("Roaming & International","Positive","Roaming worked perfectly across 3 countries. Impressed!"),
]

def gen_time_series(days=30):
    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    rows = []
    for d in dates:
        n = random.randint(40, 120)
        pos = int(n * random.uniform(0.20, 0.35))
        neg = int(n * random.uniform(0.35, 0.55))
        mix = int(n * random.uniform(0.05, 0.15))
        neu = n - pos - neg - mix
        rows.append({"date": d, "Positive": pos, "Neutral": neu, "Mixed": mix, "Negative": neg, "Total": n})
    return pd.DataFrame(rows)

def gen_category_data():
    rows = []
    for cat in CATEGORIES:
        total = random.randint(60, 250)
        neg   = int(total * random.uniform(0.3, 0.65))
        pos   = int(total * random.uniform(0.1, 0.35))
        mix   = int(total * random.uniform(0.05, 0.15))
        neu   = total - neg - pos - mix
        rows.append({"category": cat, "Positive": pos, "Neutral": neu, "Mixed": mix, "Negative": neg, "Total": total})
    return pd.DataFrame(rows).sort_values("Total", ascending=False)

df_ts   = gen_time_series(30)
df_cat  = gen_category_data()


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.5rem 0 1.5rem">
        <div style="font-size:.65rem;font-family:'IBM Plex Mono',monospace;letter-spacing:.15em;color:var(--txt-2);text-transform:uppercase">
            Brand Intelligence
        </div>
        <div style="font-size:1.05rem;font-weight:600;color:var(--txt-1);margin-top:.3rem">Analyst Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:.7rem;font-family:\'IBM Plex Mono\',monospace;letter-spacing:.1em;color:var(--txt-2);text-transform:uppercase;margin-bottom:.6rem">Filters</div>', unsafe_allow_html=True)

    date_range = st.selectbox("Time Range", ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 90 Days"])
    sentiments_filter = st.multiselect("Sentiments", SENTIMENTS, default=SENTIMENTS)
    categories_filter = st.multiselect("Categories", CATEGORIES, default=CATEGORIES)
    min_conf = st.slider("Min. Confidence %", 50, 100, 70)

    st.markdown("---")
    st.markdown('<div style="font-size:.7rem;font-family:\'IBM Plex Mono\',monospace;letter-spacing:.1em;color:var(--txt-2);text-transform:uppercase;margin-bottom:.6rem">Actions</div>', unsafe_allow_html=True)

    if st.button("🔄  Refresh Feed"):
        st.rerun()
    if st.button("📥  Export Report"):
        st.toast("Report queued for export!", icon="📄")
    if st.button("🔔  Alerts Config"):
        st.toast("Opening alert settings…", icon="⚙️")

    st.markdown("""
    <div style="position:fixed;bottom:1.5rem;font-size:.65rem;color:var(--txt-3);font-family:'IBM Plex Mono',monospace">
        TelecomAI v2.1 &nbsp;·&nbsp; NLP Engine Active
    </div>
    """, unsafe_allow_html=True)


# ─── Topbar ──────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y, %H:%M")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-logo">📊</div>
        <div>
            <div class="topbar-title">Telecom AI Brand Intelligence System</div>
            <div class="topbar-sub">Real-time Customer Sentiment & Complaint Analytics</div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:2rem">
        <div class="live-dot"><div class="dot"></div> LIVE &nbsp;· {now_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── KPI Row ─────────────────────────────────────────────────────────────────
total_fb  = int(df_ts["Total"].sum())
neg_pct   = round(df_ts["Negative"].sum() / total_fb * 100, 1)
pos_pct   = round(df_ts["Positive"].sum() / total_fb * 100, 1)
nps_score = random.randint(28, 48)

issues_pending = 0
issues_resolved = 0
try:
    feed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_root", "data", "live_feedback.json")
    if os.path.exists(feed_path):
        with open(feed_path, "r", encoding="utf-8") as f: feed_data = json.load(f)
        for item in feed_data:
            if item.get("status") == "Pending": issues_pending += 1
            elif item.get("status") == "Resolved": issues_resolved += 1
except Exception: pass

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi kpi-blue">
        <div class="kpi-label">Total Feedback</div>
        <div class="kpi-value" style="color:var(--acc-blue)">{total_fb:,}</div>
        <div class="kpi-delta"><span class="delta-pos">↑ 12.4%</span> vs prior period</div>
    </div>
    <div class="kpi kpi-red">
        <div class="kpi-label">Negative Rate</div>
        <div class="kpi-value" style="color:var(--neg)">{neg_pct}%</div>
        <div class="kpi-delta"><span class="delta-neg">↑ 3.1%</span> needs attention</div>
    </div>
    <div class="kpi kpi-green">
        <div class="kpi-label">Positive Rate</div>
        <div class="kpi-value" style="color:var(--pos)">{pos_pct}%</div>
        <div class="kpi-delta"><span class="delta-pos">↑ 2.8%</span> improving</div>
    </div>
    <div class="kpi kpi-amber">
        <div class="kpi-label">NPS Score</div>
        <div class="kpi-value" style="color:var(--neu)">{nps_score}</div>
        <div class="kpi-delta"><span class="delta-neg">↓ 4 pts</span> this period</div>
    </div>
    <div class="kpi kpi-amber">
        <div class="kpi-label">Issues Pending</div>
        <div class="kpi-value" style="color:var(--acc-amber)">{issues_pending}</div>
        <div class="kpi-delta"><span class="delta-neg">Active Tickets</span></div>
    </div>
    <div class="kpi kpi-green">
        <div class="kpi-label">Issues Resolved</div>
        <div class="kpi-value" style="color:var(--pos)">{issues_resolved}</div>
        <div class="kpi-delta"><span class="delta-pos">Closed Tickets</span></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈  Sentiment Trends", "📂  Category Analysis", "🔴  Live Feed", "🤖  AI Recommendations"])


# ── TAB 1: Sentiment Trends ──────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="sec-head">Sentiment Over Time</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        fig_line = go.Figure()
        colors = {"Positive": "#2dd4a0", "Neutral": "#f5c842", "Mixed": "#9b7dff", "Negative": "#ff5f5f"}
        
        def hex_to_rgba(hex_color, alpha):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 6:
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                return f'rgba({r},{g},{b},{alpha})'
            return hex_color

        for sent in ["Negative", "Mixed", "Neutral", "Positive"]:
            fig_line.add_trace(go.Scatter(
                x=df_ts["date"], y=df_ts[sent], name=sent,
                mode="lines", line=dict(color=colors[sent], width=2),
                fill="tozeroy", fillcolor=hex_to_rgba(colors[sent], 0.06),
                hovertemplate=f"<b>{sent}</b><br>Date: %{{x|%b %d}}<br>Count: %{{y}}<extra></extra>",
            ))
        fig_line.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            margin=dict(l=0, r=0, t=10, b=0), height=280,
            legend=dict(orientation="h", y=1.1, x=0, font=dict(color=FONT_CLR, size=11)),
            xaxis=dict(gridcolor=GRID_CLR, showline=False, tickfont=dict(color=FONT_CLR, size=10)),
            yaxis=dict(gridcolor=GRID_CLR, showline=False, tickfont=dict(color=FONT_CLR, size=10)),
            hovermode="x unified",
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="sec-head" style="margin-bottom:.6rem">Distribution</div>', unsafe_allow_html=True)
        totals = {s: int(df_ts[s].sum()) for s in ["Positive", "Neutral", "Mixed", "Negative"]}
        fig_donut = go.Figure(go.Pie(
            labels=list(totals.keys()), values=list(totals.values()),
            hole=.62, marker=dict(colors=["#2dd4a0", "#f5c842", "#9b7dff", "#ff5f5f"], line=dict(color="#07090f", width=3)),
            textinfo="none", hovertemplate="<b>%{label}</b><br>%{value} feedbacks (%{percent})<extra></extra>",
        ))
        fig_donut.update_layout(
            paper_bgcolor=PLOT_BG, margin=dict(l=0,r=0,t=0,b=0), height=220,
            showlegend=True,
            legend=dict(font=dict(color=FONT_CLR, size=10), orientation="h", y=-0.05),
            annotations=[dict(text=f"<b>{total_fb:,}</b><br><span style='font-size:9px'>total</span>",
                              x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#d8e8ff"))],
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 7-day heatmap placeholder
    st.markdown('<div class="sec-head" style="margin-top:1rem">Weekly Complaint Heatmap (Hour × Day)</div>', unsafe_allow_html=True)
    days   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours  = [f"{h:02d}:00" for h in range(0, 24, 3)]
    z_data = [[random.randint(2, 40) for _ in days] for _ in hours]
    fig_heat = go.Figure(go.Heatmap(
        z=z_data, x=days, y=hours,
        colorscale=[[0,"#0c1018"],[0.5,"#4d9fff"],[1,"#ff5f5f"]],
        hovertemplate="<b>%{x} %{y}</b><br>Complaints: %{z}<extra></extra>",
        showscale=True, colorbar=dict(tickfont=dict(color=FONT_CLR, size=9)),
    ))
    fig_heat.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, height=220,
        margin=dict(l=0,r=0,t=10,b=0),
        xaxis=dict(tickfont=dict(color=FONT_CLR, size=10)),
        yaxis=dict(tickfont=dict(color=FONT_CLR, size=10)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ── TAB 2: Category Analysis ─────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sec-head">Complaint Volume by Category</div>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        for sent, color in [("Positive","#2dd4a0"), ("Neutral","#f5c842"), ("Mixed","#9b7dff"), ("Negative","#ff5f5f")]:
            fig_bar.add_trace(go.Bar(
                name=sent, x=df_cat["category"], y=df_cat[sent],
                marker_color=color, hovertemplate=f"<b>{sent}</b><br>%{{x}}<br>Count: %{{y}}<extra></extra>",
            ))
        fig_bar.update_layout(
            barmode="stack", paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            margin=dict(l=0,r=0,t=10,b=80), height=320,
            legend=dict(orientation="h", y=1.08, font=dict(color=FONT_CLR, size=11)),
            xaxis=dict(tickfont=dict(color=FONT_CLR, size=9), tickangle=-30, gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=FONT_CLR, size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown('<div class="sec-head">Negative Sentiment Rate by Category</div>', unsafe_allow_html=True)
        df_cat["neg_rate"] = (df_cat["Negative"] / df_cat["Total"] * 100).round(1)
        df_sorted = df_cat.sort_values("neg_rate", ascending=True)
        fig_hrz = go.Figure(go.Bar(
            x=df_sorted["neg_rate"], y=df_sorted["category"],
            orientation="h",
            marker=dict(
                color=df_sorted["neg_rate"],
                colorscale=[[0,"#2dd4a0"],[0.5,"#f5c842"],[1,"#ff5f5f"]],
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>Negative Rate: %{x:.1f}%<extra></extra>",
            text=[f"{v:.1f}%" for v in df_sorted["neg_rate"]],
            textfont=dict(color=FONT_CLR, size=10),
            textposition="outside",
        ))
        fig_hrz.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            margin=dict(l=0,r=60,t=10,b=0), height=320,
            xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=FONT_CLR, size=10), range=[0, 90]),
            yaxis=dict(tickfont=dict(color=FONT_CLR, size=10)),
        )
        st.plotly_chart(fig_hrz, use_container_width=True)

    # Category table
    st.markdown('<div class="sec-head" style="margin-top:.5rem">Category Summary Table</div>', unsafe_allow_html=True)
    df_display = df_cat[["category","Total","Positive","Neutral","Mixed","Negative","neg_rate"]].copy()
    df_display.columns = ["Category","Total","✅ Positive","⚪ Neutral","🟣 Mixed","🔴 Negative","Neg Rate %"]
    df_display = df_display.sort_values("🔴 Negative", ascending=False).reset_index(drop=True)
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=280)


# ── TAB 3: Live Feed ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-head">Real-Time Feedback Monitor</div>', unsafe_allow_html=True)
    col_feed, col_spark = st.columns([3, 2])

    with col_feed:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.7rem;font-family:\'IBM Plex Mono\',monospace;color:var(--txt-2);margin-bottom:.8rem">INCOMING FEEDBACK — LAST 8 ENTRIES</div>', unsafe_allow_html=True)

        colors_dot = {"Positive": "#2dd4a0", "Neutral": "#f5c842", "Mixed": "#9b7dff", "Negative": "#ff5f5f"}
        
        feed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_root", "data", "live_feedback.json")
        live_feed = []
        try:
            if os.path.exists(feed_path):
                with open(feed_path, "r", encoding="utf-8") as f:
                    live_feed = json.load(f)
        except Exception:
            pass
            
        if not live_feed:
            # Fallback to SAMPLE_FEEDBACK
            live_feed = [{"category": c, "sentiment": s, "feedback": m, "confidence": random.randint(78,97), "timestamp": datetime.now().isoformat()} for c, s, m in SAMPLE_FEEDBACK]

        for item in live_feed[:8]:
            cat = item.get("category", "Unknown")
            sent = item.get("sentiment", "Neutral")
            msg = item.get("feedback", "")
            conf = item.get("confidence", 85)
            
            ts_str = item.get("timestamp")
            mins_ago = 0
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    mins_ago = int((datetime.now() - ts).total_seconds() / 60)
                except:
                    mins_ago = random.randint(1, 59)
            else:
                mins_ago = random.randint(1, 59)

            st.markdown(f"""
            <div class="feed-item">
                <div class="feed-dot" style="background:{colors_dot.get(sent, '#f5c842')}; box-shadow:0 0 6px {colors_dot.get(sent, '#f5c842')}40;"></div>
                <div>
                    <div class="feed-text">"{msg}"</div>
                    <div class="feed-meta">{cat} &nbsp;·&nbsp; {sent} &nbsp;·&nbsp; {mins_ago}m ago &nbsp;·&nbsp; Conf: {conf}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_spark:
        st.markdown('<div class="sec-head">Volume Spike (Last 24h)</div>', unsafe_allow_html=True)
        hours_24  = list(range(24))
        vol_24    = [random.randint(5, 80) for _ in hours_24]
        fig_spark = go.Figure(go.Bar(
            x=hours_24, y=vol_24,
            marker_color=["#ff5f5f" if v > 55 else "#4d9fff" for v in vol_24],
            hovertemplate="<b>Hour %{x}:00</b><br>Feedbacks: %{y}<extra></extra>",
        ))
        fig_spark.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            margin=dict(l=0,r=0,t=0,b=0), height=160,
            xaxis=dict(tickfont=dict(color=FONT_CLR, size=9), gridcolor=GRID_CLR),
            yaxis=dict(tickfont=dict(color=FONT_CLR, size=9), gridcolor=GRID_CLR),
            showlegend=False,
        )
        st.plotly_chart(fig_spark, use_container_width=True)

        # Top trending issues
        st.markdown('<div class="sec-head" style="margin-top:.5rem">Trending Issues</div>', unsafe_allow_html=True)
        trending = [
            ("🔴", "Signal outages — North Region", "+38%"),
            ("🔴", "Unexpected bill charges", "+22%"),
            ("🟡", "5G data throttling complaints", "+15%"),
            ("🟢", "Positive reviews — new plan", "+41%"),
        ]
        for icon, label, delta in trending:
            color = "#ff5f5f" if "🔴" in icon else ("#f5c842" if "🟡" in icon else "#2dd4a0")
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;padding:.55rem 0;border-bottom:1px solid var(--border);font-size:.78rem;">
                <span>{icon} &nbsp;{label}</span>
                <span style="color:{color};font-family:'IBM Plex Mono',monospace;font-size:.72rem;">{delta}</span>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 4: AI Recommendations ────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-head">AI-Generated Insights & Recommendations</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(77,159,255,.07);border:1px solid rgba(77,159,255,.2);border-radius:10px;padding:1rem 1.2rem;margin-bottom:1.2rem;font-size:.82rem;color:var(--txt-2);line-height:1.6;">
        🤖 <b style="color:var(--txt-1)">TelecomAI Analysis Engine</b> — Based on the past 30 days of customer feedback across 8 service categories, the following prioritized recommendations have been identified using NLP pattern analysis and RAG-augmented policy review.
    </div>
    """, unsafe_allow_html=True)

    recommendations = [
        ("🌐", "URGENT — Network Infrastructure Review",
         "Network Connectivity accounts for 42% of all negative feedback, with spike patterns between 18:00–22:00 indicating capacity constraints in urban zones. Cross-referenced with Service SLA Policy v3.2 — current resolution times exceed the committed 4-hour window.",
         "HIGH PRIORITY"),
        ("💳", "Billing Transparency Initiative",
         "28% of billing complaints cite 'unexpected charges' with no prior notification. RAG retrieval of Billing Policy 2024 confirms that proactive SMS/email alerts for charges above ₹500 are mandated but not consistently triggered.",
         "PROCESS GAP"),
        ("📶", "5G Data Fair-Use Communication",
         "Customer confusion around data throttling after quota exhaustion suggests the Fair Usage Policy is not visible at point of sale or within the app. Recommend in-app notification 3 days before quota limit.",
         "CX IMPROVEMENT"),
        ("🎧", "Customer Support Training Refresh",
         "Sentiment recovery rate after support interactions is 34% — below the 60% industry benchmark. Analysis indicates recurring issues with first-call resolution. Recommend targeted training on Network and Billing categories.",
         "TRAINING NEEDED"),
        ("🌍", "Roaming Onboarding Experience",
         "Despite strong positive sentiment (67%), roaming-related queries spike 3x before international travel periods. Proactive pre-travel SMS campaigns could reduce inbound support volume by ~25%.",
         "QUICK WIN"),
    ]

    priority_colors = {
        "HIGH PRIORITY": "#ff5f5f",
        "PROCESS GAP": "#f5c842",
        "CX IMPROVEMENT": "#4d9fff",
        "TRAINING NEEDED": "#9b7dff",
        "QUICK WIN": "#2dd4a0",
    }

    for icon, title, body, tag in recommendations:
        color = priority_colors.get(tag, "#4d9fff")
        st.markdown(f"""
        <div class="rec-card" style="border-left-color:{color}">
            <div class="rec-icon">{icon}</div>
            <div>
                <div class="rec-title">{title}</div>
                <div class="rec-body">{body}</div>
                <span class="tag" style="background:rgba(0,0,0,.2);border-color:{color}40;color:{color}">{tag}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Impact matrix
    st.markdown('<div class="sec-head" style="margin-top:1.5rem">Effort vs Impact Matrix</div>', unsafe_allow_html=True)
    items = [
        ("In-app quota alerts", 2, 8, "Data Services"),
        ("Billing SMS triggers", 3, 7.5, "Billing"),
        ("Network infra upgrade", 9, 9.5, "Network"),
        ("Support training", 4, 6.5, "Support"),
        ("Roaming campaigns", 2.5, 5.5, "Roaming"),
    ]
    df_impact = pd.DataFrame(items, columns=["Initiative","Effort","Impact","Category"])
    cat_colors = {
        "Data Services": "#4d9fff", "Billing": "#f5c842",
        "Network": "#ff5f5f", "Support": "#9b7dff", "Roaming": "#2dd4a0",
    }
    fig_scatter = go.Figure()
    for _, row in df_impact.iterrows():
        fig_scatter.add_trace(go.Scatter(
            x=[row["Effort"]], y=[row["Impact"]], mode="markers+text",
            name=row["Initiative"],
            text=[row["Initiative"]], textposition="top center",
            textfont=dict(color=FONT_CLR, size=9),
            marker=dict(size=20, color=cat_colors.get(row["Category"], "#4d9fff"), opacity=.85,
                        line=dict(width=1, color="rgba(255,255,255,.2)")),
        ))
    fig_scatter.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        margin=dict(l=0,r=0,t=10,b=0), height=300, showlegend=False,
        xaxis=dict(title="Implementation Effort →", gridcolor=GRID_CLR, tickfont=dict(color=FONT_CLR, size=10),
                   range=[0,11], title_font=dict(color=FONT_CLR, size=11)),
        yaxis=dict(title="Customer Impact →", gridcolor=GRID_CLR, tickfont=dict(color=FONT_CLR, size=10),
                   range=[0,11], title_font=dict(color=FONT_CLR, size=11)),
    )
    # Add quadrant lines
    fig_scatter.add_hline(y=5.5, line=dict(color=GRID_CLR, dash="dot"))
    fig_scatter.add_vline(x=5.5, line=dict(color=GRID_CLR, dash="dot"))
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:2rem;padding:1rem;border-top:1px solid var(--border);
     color:var(--txt-3);font-size:.68rem;font-family:'IBM Plex Mono',monospace;letter-spacing:.08em">
    TELECOMAI BRAND INTELLIGENCE SYSTEM &nbsp;·&nbsp; ANALYST DASHBOARD v2.1 &nbsp;·&nbsp; NLP + RAG ENGINE ACTIVE
</div>
""", unsafe_allow_html=True)
