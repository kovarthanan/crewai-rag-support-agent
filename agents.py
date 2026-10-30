"""Agent definitions: Agent 1 (vector DB), Agent 2 (web search), Agent 3 (logger)."""

import os

from crewai import LLM, Agent
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

from tools import CompanyPolicySearchTool, LogWriterTool

load_dotenv()


def get_llm() -> LLM:
    return LLM(model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"), temperature=0)


def create_knowledge_agent() -> Agent:
    """Agent 1 - answers only from the FAISS vector DB."""
    return Agent(
        role="Company Knowledge Base Specialist",
        goal=(
            "Answer employee questions accurately using ONLY NovaWave Technologies' "
            "internal documents, and honestly report when the documents do not contain the answer."
        ),
        backstory=(
            "You are NovaWave's HR and IT help-desk expert. You never guess or use outside "
            "knowledge. You always search the company documents first, quote exact numbers "
            "and policy names, and say clearly when something is not covered."
        ),
        tools=[CompanyPolicySearchTool()],
        llm=get_llm(),
        allow_delegation=False,
        max_iter=4,
        verbose=True,
    )


def create_web_search_agent() -> Agent:
    """Agent 2 - fallback: searches the public web when Agent 1 is not satisfied."""
    search_tool = SerperDevTool(
        n_results=5,
        country="in",   # India-focused results (EPF, tax slabs, labour law...)
    )
    return Agent(
        role="Web Research Support Specialist",
        goal=(
            "Find accurate, up-to-date answers on the public web for employee questions "
            "that the company documents could not answer, and always cite the sources."
        ),
        backstory=(
            "You are a careful researcher. You prefer official sources (government sites, "
            "regulators, official company pages) over blogs and forums, you never invent "
            "facts, and you make it clear the answer comes from the web, not NovaWave policy."
        ),
        tools=[search_tool],
        llm=get_llm(),
        allow_delegation=False,
        max_iter=5,
        verbose=True,
    )


def create_logger_agent() -> Agent:
    """Agent 3 - writes every question and its final answer to the log file."""
    return Agent(
        role="Support Interaction Logger",
        goal=(
            "Record every employee question and the final answer that was given, "
            "accurately and completely, in the support log file."
        ),
        backstory=(
            "You are a meticulous audit clerk. You never change, shorten or invent an answer; "
            "you copy exactly what was delivered to the employee and note which agent answered it."
        ),
        tools=[LogWriterTool(result_as_answer=True)],  # tool output becomes the task result
        llm=get_llm(),
        allow_delegation=False,
        max_iter=3,
        verbose=True,
    )
