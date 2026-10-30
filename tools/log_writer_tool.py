"""
Custom crewAI tool used by Agent 3: appends one Q&A entry to a text log file.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

LOG_FILE = Path(os.getenv("LOG_FILE", "logs/support_log.txt"))
SEPARATOR = "-" * 70


class LogEntryInput(BaseModel):
    """Input schema for the log writer tool."""
    question: str = Field(..., description="The employee's original question, word for word.")
    answered_by: str = Field(
        ...,
        description="Exactly one of: 'Knowledge Base (Agent 1)' or 'Web Search (Agent 2)'.",
    )
    answer: str = Field(..., description="The final answer given to the employee.")
    sources: str = Field(..., description="Comma-separated sources (document > section, or URLs).")
    confidence: str = Field(
        "N/A", description="Agent 1's similarity score, e.g. '0.502'. Use 'N/A' if unknown."
    )
    status: str = Field(
        ...,
        description="'RESOLVED' if a reliable answer was given, otherwise 'UNRESOLVED'.",
    )


class LogWriterTool(BaseTool):
    name: str = "support_log_writer"
    description: str = (
        "Appends one question-and-answer record to the customer support log file. "
        "Call it exactly ONCE per question with all fields filled in."
    )
    args_schema: Type[BaseModel] = LogEntryInput

    def _run(
        self,
        question: str,
        answered_by: str,
        answer: str,
        sources: str,
        confidence: str = "N/A",
        status: str = "RESOLVED",
    ) -> str:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = (
            f"[{timestamp}]\n"
            f"QUESTION    : {question.strip()}\n"
            f"ANSWERED BY : {answered_by.strip()}\n"
            f"STATUS      : {status.strip().upper()}\n"
            f"CONFIDENCE  : {confidence.strip()}\n"
            f"SOURCES     : {sources.strip() or '-'}\n"
            f"ANSWER      : {answer.strip()}\n"
            f"{SEPARATOR}\n"
        )

        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(entry)

        return f"Logged successfully to {LOG_FILE} at {timestamp}."
