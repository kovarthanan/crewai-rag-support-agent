"""
Step 4 - Test Agent 1 on its own.

Run:
  python test_agent1.py
  python test_agent1.py "Can I accept a gift from a vendor?"
"""

import sys

from crewai import Crew, Process

from agents import create_knowledge_agent
from tasks import create_knowledge_task

DEFAULT_QUESTIONS = [
    "How many sick leaves do I get and do I need a medical certificate?",  # in docs
    "What is the current EPF interest rate in India?",                    # NOT in docs
]


def ask(question: str):
    agent = create_knowledge_agent()
    task = create_knowledge_task(agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    result = crew.kickoff(inputs={"question": question})
    out = result.pydantic  # KnowledgeBaseAnswer

    print("\n" + "=" * 70)
    print(f"QUESTION    : {question}")
    print(f"ANSWER      : {out.answer}")
    print(f"SATISFIED   : {out.is_satisfied}")
    print(f"CONFIDENCE  : {out.confidence:.3f}")
    print(f"SOURCES     : {', '.join(out.sources) or '-'}")
    print(f"REASON      : {out.reason}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else DEFAULT_QUESTIONS
    for q in questions:
        ask(q)
