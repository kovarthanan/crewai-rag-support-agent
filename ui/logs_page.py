"""Support Log page - every logged Q&A in a searchable table."""

import streamlit as st

from ui.log_parser import LOG_FILE, parse_log
from ui.styles import badge, hero

hero("📋 Support Log", "Every question asked and the answer given, as recorded by the logging agent.")

df = parse_log()

if df.empty:
    st.info(f"No log entries yet. Ask a question on the Chat page — entries appear in `{LOG_FILE}`.")
    st.stop()

# ------------------------------------------------------------------ metrics
total = len(df)
kb_share = df["Answered By"].str.startswith("Knowledge").mean()
resolved = (df["Status"] == "RESOLVED").mean()
avg_conf = df["Confidence"].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total questions", f"{total}")
m2.metric("Answered from policy", f"{kb_share:.0%}")
m3.metric("Resolved", f"{resolved:.0%}")
m4.metric("Avg. match score", f"{avg_conf:.2f}" if avg_conf == avg_conf else "–")

st.write("")

# ------------------------------------------------------------------ filters
f1, f2, f3 = st.columns([2, 1, 1])
search = f1.text_input("🔎 Search questions & answers", placeholder="e.g. leave, gift, EPF")
source_opt = f2.selectbox("Answered by", ["All", "Knowledge Base (Agent 1)", "Web Search (Agent 2)"])
status_opt = f3.selectbox("Status", ["All", "RESOLVED", "UNRESOLVED"])

dmin, dmax = df["Timestamp"].min().date(), df["Timestamp"].max().date()
date_range = st.date_input("Date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)

view = df.copy()
if search:
    mask = (view["Question"].str.contains(search, case=False, na=False)
            | view["Answer"].str.contains(search, case=False, na=False))
    view = view[mask]
if source_opt != "All":
    view = view[view["Answered By"] == source_opt]
if status_opt != "All":
    view = view[view["Status"] == status_opt]
if isinstance(date_range, tuple) and len(date_range) == 2:
    d0, d1 = date_range
    view = view[(view["Timestamp"].dt.date >= d0) & (view["Timestamp"].dt.date <= d1)]
view = view.reset_index(drop=True)
view["Result"] = view["Status"].map({"RESOLVED": "✅ Resolved", "UNRESOLVED": "⚠️ Unresolved"}).fillna(view["Status"])
view["Source"] = view["Answered By"].map(
    {"Knowledge Base (Agent 1)": "📚 Policy", "Web Search (Agent 2)": "🌐 Web"}).fillna(view["Answered By"])

# ------------------------------------------------------------------ table
st.caption(f"Showing {len(view)} of {total} entries · click a row to see the full answer")

event = st.dataframe(
    view,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    column_order=["Timestamp", "Question", "Source", "Result", "Confidence"],
    column_config={
        "Timestamp": st.column_config.DatetimeColumn("Time", format="DD MMM YYYY, hh:mm a"),
        "Question": st.column_config.TextColumn("Question", width="large"),
        "Source": st.column_config.TextColumn("Answered by"),
        "Result": st.column_config.TextColumn("Status"),
        "Confidence": st.column_config.ProgressColumn(
            "Match score", min_value=0.0, max_value=1.0, format="%.2f"
        ),
    },
)

# ------------------------------------------------------------------ detail panel
rows = event.selection.rows if event and event.selection else []
if rows:
    r = view.iloc[rows[0]]
    is_kb = r["Answered By"].startswith("Knowledge")
    with st.container(border=True):
        st.markdown(
            badge("📚 Company Policy" if is_kb else "🌐 Web Search", "kb" if is_kb else "web")
            + badge(r["Status"].title(), "ok" if r["Status"] == "RESOLVED" else "bad")
            + badge(r["Timestamp"].strftime("%d %b %Y, %I:%M %p"), "conf"),
            unsafe_allow_html=True,
        )
        st.markdown(f"**Q: {r['Question']}**")
        st.markdown(r["Answer"])
        st.caption(f"Sources: {r['Sources']}")

# ------------------------------------------------------------------ export
st.download_button(
    "⬇️  Export as CSV",
    view[["Timestamp", "Question", "Answered By", "Status", "Confidence", "Sources", "Answer"]].to_csv(index=False).encode("utf-8"),
    file_name="support_log.csv",
    mime="text/csv",
)
