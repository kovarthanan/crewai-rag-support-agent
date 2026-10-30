"""Chat page - employees ask questions, the crew answers."""

import streamlit as st

from main import answer_question
from ui.styles import badge, hero

SAMPLE_QUESTIONS = [
    ("🤒 Leave", "How many sick leaves do I get?"),
    ("🎁 Ethics", "Can I accept a gift from a vendor?"),
    ("🏢 Hybrid work", "How many days do I need to work from office?"),
    ("💰 Payroll", "When is salary credited?"),
]

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_meta(meta: dict):
    is_kb = meta["answered_by"].startswith("Knowledge")
    html = badge("📚 Company Policy" if is_kb else "🌐 Web Search", "kb" if is_kb else "web")
    html += badge(f"Match {meta['confidence']:.0%}", "conf")
    st.markdown(html, unsafe_allow_html=True)

    if meta["sources"]:
        with st.expander("Sources"):
            for s in meta["sources"]:
                st.markdown(f"- [{s}]({s})" if s.startswith("http") else f"- {s}")


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("#### Try asking")
    for label, q in SAMPLE_QUESTIONS:
        if st.button(q, key=f"side_{q}", use_container_width=True):
            st.session_state.pending = q
    st.divider()
    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ------------------------------------------------------------------ header
hero(
    "💬 NovaWave Support Assistant",
    "Instant answers on HR, leave, hybrid work, IT & security and code of conduct — "
    "straight from company policy.",
)

# Welcome cards when the conversation is empty
if not st.session_state.messages:
    cols = st.columns(len(SAMPLE_QUESTIONS))
    for col, (label, q) in zip(cols, SAMPLE_QUESTIONS):
        with col:
            st.markdown(f'<div class="nw-card"><b>{label}</b><p>{q}</p></div>',
                        unsafe_allow_html=True)
            if st.button("Ask", key=f"card_{q}", use_container_width=True):
                st.session_state.pending = q
    st.caption("Answers come from company documents first. If a question isn't covered, "
               "the assistant searches the web and labels the answer clearly.")

# History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "💜"):
        st.markdown(msg["content"])
        if msg.get("meta"):
            render_meta(msg["meta"])

# ------------------------------------------------------------------ input
question = st.chat_input("Ask a question about company policies...")
if not question and st.session_state.get("pending"):
    question = st.session_state.pop("pending")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="💜"):
        with st.spinner("Searching company policies..."):
            try:
                result = answer_question(question)
            except Exception as e:
                st.error(f"Sorry, something went wrong: {e}")
                st.stop()
        st.markdown(result["answer"])
        render_meta(result)

    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "meta": result}
    )
    st.rerun()
