"""Parse logs/support_log.txt (written by Agent 3) into a pandas DataFrame."""

import os
import re
from pathlib import Path

import pandas as pd

LOG_FILE = Path(os.getenv("LOG_FILE", "logs/support_log.txt"))

COLUMNS = ["Timestamp", "Question", "Answered By", "Status", "Confidence", "Sources", "Answer"]
_FIELDS = {
    "QUESTION": "Question",
    "ANSWERED BY": "Answered By",
    "STATUS": "Status",
    "CONFIDENCE": "Confidence",
    "SOURCES": "Sources",
    "ANSWER": "Answer",
}
_ENTRY_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s*$", re.MULTILINE)
_FIELD_RE = re.compile(r"^(QUESTION|ANSWERED BY|STATUS|CONFIDENCE|SOURCES|ANSWER)\s*:\s?(.*)$")


def parse_log(path: Path = LOG_FILE) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)

    text = path.read_text(encoding="utf-8")
    starts = list(_ENTRY_RE.finditer(text))
    rows = []

    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        body = text[m.end():end]
        body = re.sub(r"\n-{10,}\s*$", "", body.rstrip())   # drop trailing separator

        row = {"Timestamp": m.group(1)}
        current = None
        for line in body.splitlines():
            fm = _FIELD_RE.match(line)
            # ANSWER is the last field and may span many lines
            if fm and current != "Answer":
                current = _FIELDS[fm.group(1)]
                row[current] = fm.group(2).strip()
            elif current:
                row[current] = (row.get(current, "") + "\n" + line).strip()
        rows.append(row)

    df = pd.DataFrame(rows).reindex(columns=COLUMNS)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Confidence"] = pd.to_numeric(df["Confidence"], errors="coerce")
    df["Status"] = df["Status"].fillna("").str.upper()
    df["Answered By"] = df["Answered By"].fillna("")
    return df.sort_values("Timestamp", ascending=False).reset_index(drop=True)
