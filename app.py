"""
NovaWave Support - Streamlit entry point (violet theme, 2 pages).

Run from the project root:
  streamlit run app.py
"""

import streamlit as st

from ui.styles import apply_theme

st.set_page_config(page_title="NovaWave Support", page_icon="💜", layout="wide")
apply_theme()
st.logo("ui/logo.svg", size="large")

chat = st.Page("ui/chat_page.py", title="Ask Support", icon="💬", default=True)
logs = st.Page("ui/logs_page.py", title="Support Log", icon="📋")

nav = st.navigation([chat, logs])
nav.run()

with st.sidebar:
    st.caption("📚 Policy search → 🌐 Web fallback → 📝 Logged")
