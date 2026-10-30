"""Structured outputs returned by the agents."""

from pydantic import BaseModel, Field


class KnowledgeBaseAnswer(BaseModel):
    """Output of Agent 1 (vector DB agent)."""
    answer: str = Field(..., description="Answer for the employee, based only on the company documents.")
    is_satisfied: bool = Field(
        ..., description="True only if the company documents fully answer the question."
    )
    confidence: float = Field(..., ge=0, le=1, description="Best similarity score from the search tool (0-1).")
    sources: list[str] = Field(default_factory=list, description="Document > section used for the answer.")
    reason: str = Field(..., description="One line: why the answer is or is not satisfied.")


class WebSearchAnswer(BaseModel):
    """Output of Agent 2 (web search agent)."""
    answer: str = Field(..., description="Answer for the employee based on web search results.")
    sources: list[str] = Field(default_factory=list, description="URLs of the web pages used.")
    found: bool = Field(..., description="True if the web search produced a reliable answer.")
    disclaimer: str = Field(
        ...,
        description="Short note telling the employee this came from the public web, not company policy.",
    )
