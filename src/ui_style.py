from __future__ import annotations

import streamlit as st


def apply_tech_style() -> None:
    st.markdown(
        """
<style>
:root {
    --primary-blue: #0B5CFF;
    --deep-blue: #073B8E;
    --soft-blue: #F7FBFF;
    --line-blue: #D7E7FF;
    --text-main: #0F172A;
    --text-muted: #64748B;
}

.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(11, 92, 255, 0.11), transparent 25%),
        radial-gradient(circle at 95% 2%, rgba(56, 189, 248, 0.13), transparent 25%),
        linear-gradient(180deg, #F8FBFF 0%, #FFFFFF 45%, #F7FBFF 100%);
    color: var(--text-main);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2.4rem;
    max-width: 1380px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F8FBFF 0%, #EEF6FF 100%);
    border-right: 1px solid var(--line-blue);
}
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--deep-blue); }

h1, h2, h3 { color: #082B62; letter-spacing: -0.02em; }

.hero-card {
    position: relative;
    overflow: hidden;
    border-radius: 26px;
    padding: 24px 30px;
    background: linear-gradient(135deg, #0B5CFF 0%, #0E7CFF 52%, #38BDF8 100%);
    color: white;
    box-shadow: 0 18px 46px rgba(11, 92, 255, 0.20);
    margin-bottom: 22px;
}
.hero-card:after {
    content: "";
    position: absolute;
    width: 330px;
    height: 330px;
    right: -120px;
    top: -130px;
    border-radius: 999px;
    background: rgba(255,255,255,0.14);
}
.hero-title { font-size: 29px; font-weight: 820; line-height: 1.18; margin-bottom: 8px; }
.hero-subtitle { max-width: 900px; font-size: 15px; color: rgba(255,255,255,0.88); }
.hero-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    font-size: 13px;
    margin-bottom: 10px;
}

.panel-card {
    background: rgba(255, 255, 255, 0.90);
    border: 1px solid var(--line-blue);
    border-radius: 24px;
    padding: 22px 24px;
    box-shadow: 0 14px 36px rgba(15, 82, 186, 0.075);
    margin-bottom: 22px;
}

.step-card {
    border: 1px solid #CFE2FF;
    border-radius: 24px;
    padding: 22px 24px;
    background: linear-gradient(180deg, #FFFFFF 0%, #F3F8FF 100%);
    box-shadow: 0 14px 34px rgba(8, 73, 160, 0.08);
    margin-bottom: 20px;
}
.step-card b { color: #073B8E; }
.step-title { font-size: 19px; font-weight: 760; color: #073B8E; margin-bottom: 10px; }
.step-chip {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    color: #0750B8;
    background: #EAF3FF;
    border: 1px solid #CFE2FF;
    font-size: 12px;
    margin-bottom: 12px;
}

.info-strip {
    padding: 16px 18px;
    border-radius: 18px;
    background: #F0F7FF;
    border: 1px solid #CFE2FF;
    color: #12376B;
    margin-bottom: 18px;
    line-height: 1.72;
}
.kb-box {
    padding: 16px 18px;
    border-radius: 18px;
    background: linear-gradient(135deg, #F7FBFF 0%, #FFFFFF 100%);
    border: 1px dashed #AFCFFF;
    color: #1E3A5F;
    margin-bottom: 18px;
    line-height: 1.72;
}

.compact-note { color: var(--text-muted); font-size: 13px; line-height: 1.65; }

.risk-high, .risk-medium, .risk-low {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 800;
}
.risk-high { color:#B42318; background:#FEF3F2; border:1px solid #FECDCA; }
.risk-medium { color:#B54708; background:#FFFAEB; border:1px solid #FEDF89; }
.risk-low { color:#027A48; background:#ECFDF3; border:1px solid #ABEFC6; }

.stButton > button {
    border-radius: 13px;
    border: 1px solid #BFD8FF;
    background: linear-gradient(180deg, #FFFFFF 0%, #F2F7FF 100%);
    color: #0A3A7A;
    font-weight: 650;
    box-shadow: 0 6px 14px rgba(11, 92, 255, 0.07);
    min-height: 2.55rem;
}
.stButton > button:hover { border-color: #0B5CFF; color: #0B5CFF; }
.stDownloadButton > button {
    border-radius: 13px;
    background: linear-gradient(135deg, #0B5CFF 0%, #1688FF 100%);
    color: white;
    border: none;
    font-weight: 720;
    box-shadow: 0 10px 24px rgba(11, 92, 255, 0.18);
    min-height: 2.55rem;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.84);
    border: 1px solid var(--line-blue);
    border-radius: 20px;
    padding: 15px 17px;
    box-shadow: 0 12px 30px rgba(15, 82, 186, 0.07);
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div {
    border-radius: 13px;
    border-color: #CFE2FF;
    background-color: rgba(255,255,255,0.94);
}

[data-testid="stExpander"] {
    border: 1px solid var(--line-blue);
    border-radius: 17px;
    background: rgba(255,255,255,0.88);
    box-shadow: 0 8px 22px rgba(15, 82, 186, 0.055);
    margin-bottom: 12px;
}

hr { border-color: #D7E7FF; margin: 1.5rem 0; }
.footer-note { text-align: center; color: #64748B; font-size: 13px; padding: 18px 0 4px; }
</style>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, badge: str = "AI Guided Audit SOP") -> None:
    st.markdown(
        f"""
<div class="hero-card">
  <div class="hero-badge">{badge}</div>
  <div class="hero-title">{title}</div>
  <div class="hero-subtitle">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )
