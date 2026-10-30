"""
Step 5 - Test Agent 1 + Agent 2 together.

Agent 2 (web search) runs ONLY when Agent 1 returns is_satisfied = False.

Run:
  python test_agent2.py
  python test_agent2.py "What is the new income tax regime slab for FY 2026-27?"
"""

import sys

from crewai import Crew, Process

from agents import create_knowledge_agent, create_web_search_agent
from tasks import create_knowledge_task, create_web_search_task

DEFAULT_QUESTIONS = [
    "How many sick leaves do I get?",                        # -> Agent 1 only
    "What is the current EPF interest rate in India?",        # -> Agent 1 fails -> Agent 2
]


def ask(question: str):
    kb_agent = create_knowledge_agent()
    web_agent = create_web_search_agent()

    kb_task = create_knowledge_task(kb_agent)
    web_task = create_web_search_task(web_agent, kb_task)

    crew = Crew(
        agents=[kb_agent, web_agent],
        tasks=[kb_task, web_task],
        process=Process.sequential,
        verbose=False,
    )
    crew.kickoff(inputs={"question": question})

    kb = kb_task.output.pydantic
    web_out = web_task.output
    web_ran = web_out is not None and web_out.raw != ""   # skipped task -> empty raw

    print("\n" + "=" * 70)
    print(f"QUESTION     : {question}")
    print(f"AGENT 1      : satisfied={kb.is_satisfied}  confidence={kb.confidence:.3f}")

    if not web_ran:
        print("ANSWERED BY  : Knowledge Base (Agent 1)")
        print(f"ANSWER       : {kb.answer}")
        print(f"SOURCES      : {', '.join(kb.sources) or '-'}")
    else:
        web = web_out.pydantic
        print(f"AGENT 1 NOTE : {kb.reason}")
        print("ANSWERED BY  : Web Search (Agent 2)")
        print(f"ANSWER       : {web.answer}")
        print(f"SOURCES      : {', '.join(web.sources) or '-'}")
        print(f"FOUND        : {web.found}")
        print(f"DISCLAIMER   : {web.disclaimer}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else DEFAULT_QUESTIONS
    for q in questions:
        ask(q)
