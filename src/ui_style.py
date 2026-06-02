from __future__ import annotations

import streamlit as st


def apply_tech_style() -> None:
    st.markdown(
        """
<style>
:root {
    --primary-blue: #0B5CFF;
    --deep-blue: #073B8E;
    --sky-blue: #EAF3FF;
    --soft-blue: #F6FAFF;
    --line-blue: #D7E7FF;
    --text-main: #0F172A;
    --text-muted: #64748B;
    --white: #FFFFFF;
}

.stApp {
    background:
        radial-gradient(circle at 12% 0%, rgba(11, 92, 255, 0.14), transparent 26%),
        radial-gradient(circle at 88% 4%, rgba(56, 189, 248, 0.15), transparent 25%),
        linear-gradient(180deg, #F8FBFF 0%, #FFFFFF 44%, #F7FBFF 100%);
    color: var(--text-main);
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F7FBFF 0%, #EEF6FF 100%);
    border-right: 1px solid var(--line-blue);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--deep-blue);
}

h1, h2, h3 {
    color: #082B62;
    letter-spacing: -0.02em;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--line-blue);
    border-radius: 18px;
    padding: 14px 16px;
    box-shadow: 0 12px 34px rgba(15, 82, 186, 0.08);
}

.hero-card {
    position: relative;
    overflow: hidden;
    border-radius: 24px;
    padding: 24px 28px;
    background: linear-gradient(135deg, #0B5CFF 0%, #0E7CFF 48%, #39BDF8 100%);
    color: white;
    box-shadow: 0 18px 50px rgba(11, 92, 255, 0.22);
    margin-bottom: 18px;
}
.hero-card:after {
    content: "";
    position: absolute;
    width: 320px;
    height: 320px;
    right: -95px;
    top: -115px;
    border-radius: 999px;
    background: rgba(255,255,255,0.16);
}
.hero-title {
    font-size: 30px;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 8px;
}
.hero-subtitle {
    max-width: 920px;
    font-size: 15px;
    color: rgba(255,255,255,0.88);
}
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
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid var(--line-blue);
    border-radius: 22px;
    padding: 18px 20px;
    box-shadow: 0 14px 38px rgba(15, 82, 186, 0.08);
    margin-bottom: 16px;
}

.step-card {
    border: 1px solid #CFE2FF;
    border-radius: 22px;
    padding: 18px 20px;
    background: linear-gradient(180deg, #FFFFFF 0%, #F3F8FF 100%);
    box-shadow: 0 14px 34px rgba(8, 73, 160, 0.09);
    margin-bottom: 14px;
}
.step-card b { color: #073B8E; }
.step-title {
    font-size: 18px;
    font-weight: 750;
    color: #073B8E;
    margin-bottom: 8px;
}
.step-chip {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    color: #0750B8;
    background: #EAF3FF;
    border: 1px solid #CFE2FF;
    font-size: 12px;
    margin-bottom: 10px;
}

.info-strip {
    padding: 14px 16px;
    border-radius: 18px;
    background: #F0F7FF;
    border: 1px solid #CFE2FF;
    color: #12376B;
    margin-bottom: 14px;
}

.kb-box {
    padding: 14px 16px;
    border-radius: 18px;
    background: linear-gradient(135deg, #F7FBFF 0%, #FFFFFF 100%);
    border: 1px dashed #AFCFFF;
    color: #1E3A5F;
    margin-bottom: 14px;
}

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
    border-radius: 12px;
    border: 1px solid #BFD8FF;
    background: linear-gradient(180deg, #FFFFFF 0%, #F2F7FF 100%);
    color: #0A3A7A;
    font-weight: 650;
    box-shadow: 0 6px 14px rgba(11, 92, 255, 0.08);
}
.stButton > button:hover {
    border-color: #0B5CFF;
    color: #0B5CFF;
    box-shadow: 0 8px 18px rgba(11, 92, 255, 0.14);
}

.stDownloadButton > button {
    border-radius: 12px;
    background: linear-gradient(135deg, #0B5CFF 0%, #1688FF 100%);
    color: white;
    border: none;
    font-weight: 700;
    box-shadow: 0 10px 24px rgba(11, 92, 255, 0.20);
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div {
    border-radius: 12px;
    border-color: #CFE2FF;
    background-color: rgba(255,255,255,0.92);
}

[data-testid="stExpander"] {
    border: 1px solid var(--line-blue);
    border-radius: 16px;
    background: rgba(255,255,255,0.86);
    box-shadow: 0 8px 24px rgba(15, 82, 186, 0.06);
}

hr {
    border-color: #D7E7FF;
}

.small-note {
    color: var(--text-muted);
    font-size: 13px;
}

.footer-note {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    padding: 18px 0 4px;
}
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


def section_card_start(title: str | None = None) -> None:
    if title:
        st.markdown(f"<div class='panel-card'><div class='step-title'>{title}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)


def section_card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
