"""Shared violet theme CSS and small HTML helpers for all pages."""

import streamlit as st

VIOLET_900 = "#4C1D95"
VIOLET_700 = "#6D28D9"
VIOLET_600 = "#7C3AED"
VIOLET_400 = "#A78BFA"
VIOLET_100 = "#EDE9FE"
VIOLET_50 = "#F5F3FF"

CSS = f"""
<style>
/* ---------- layout ---------- */
.block-container, [data-testid="stMainBlockContainer"] {{ padding-top: 4.5rem; max-width: 1280px; }}
[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stAppDeployButton"] {{ display: none; }}
[data-testid="stSidebarHeader"] img {{ height: 2.6rem; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {VIOLET_900} 0%, {VIOLET_700} 100%);
}}
[data-testid="stSidebar"] * {{ color: #F5F3FF !important; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2); }}
[data-testid="stSidebar"] .stButton button {{
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.25);
    text-align: left; justify-content: flex-start;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background: rgba(255,255,255,0.22); border-color: #fff;
}}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: rgba(255,255,255,0.18); border-radius: 8px;
}}

/* ---------- hero banner ---------- */
.nw-hero {{
    background: linear-gradient(120deg, {VIOLET_900} 0%, {VIOLET_600} 55%, {VIOLET_400} 100%);
    border-radius: 18px; padding: 1.6rem 1.8rem; color: #fff; margin-bottom: 1.4rem;
    box-shadow: 0 10px 30px rgba(124,58,237,0.25);
}}
.nw-hero h1 {{ color: #fff; font-size: 1.8rem; margin: 0 0 .3rem 0; padding: 0; }}
.nw-hero p  {{ color: #EDE9FE; margin: 0; font-size: .98rem; }}

/* ---------- chat ---------- */
[data-testid="stChatMessage"] {{
    border-radius: 14px; padding: .9rem 1rem; margin-bottom: .6rem;
    border: 1px solid {VIOLET_100};
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: {VIOLET_50};
}}
[data-testid="stChatInput"] textarea {{ border-radius: 12px; }}

/* ---------- badges ---------- */
.nw-badge {{
    display: inline-block; padding: .22rem .7rem; border-radius: 999px;
    font-size: .78rem; font-weight: 600; margin-right: .4rem;
}}
.nw-kb   {{ background: {VIOLET_100}; color: {VIOLET_700}; }}
.nw-web  {{ background: #E0F2FE; color: #0369A1; }}
.nw-conf {{ background: #F1F5F9; color: #334155; }}
.nw-ok   {{ background: #DCFCE7; color: #15803D; }}
.nw-bad  {{ background: #FEE2E2; color: #B91C1C; }}

/* ---------- metric cards ---------- */
[data-testid="stMetric"] {{
    background: #fff; border: 1px solid {VIOLET_100}; border-left: 5px solid {VIOLET_600};
    border-radius: 14px; padding: .9rem 1rem; box-shadow: 0 2px 8px rgba(76,29,149,0.06);
}}
[data-testid="stMetricLabel"] p {{ color: #6B7280; font-weight: 600; }}
[data-testid="stMetricValue"] {{ color: {VIOLET_900}; }}

/* ---------- welcome cards ---------- */
.nw-card {{
    border: 1px solid {VIOLET_100}; border-radius: 14px; padding: 1rem;
    background: #fff; min-height: 132px; margin-bottom: .5rem;
}}
.nw-card b {{ color: {VIOLET_700}; }}
.nw-card p {{ color: #4B5563; font-size: .88rem; margin: .3rem 0 0 0; }}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(
        f'<div class="nw-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str) -> str:
    return f'<span class="nw-badge nw-{kind}">{text}</span>'
