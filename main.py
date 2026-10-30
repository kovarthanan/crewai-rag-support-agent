"""
Step 6 - Full customer support crew (Agent 1 -> Agent 2 if needed -> Agent 3 logs).

Run:
  python main.py                                   # interactive chat (type 'exit' to quit)
  python main.py "How many casual leaves do I get?"  # single question
"""

import os
import sys

from crewai import Crew, Process

from agents import create_knowledge_agent, create_logger_agent, create_web_search_agent
from tasks import create_knowledge_task, create_logging_task, create_web_search_task

VERBOSE = os.getenv("CREW_VERBOSE", "false").lower() == "true"


def build_crew():
    """Build a fresh crew per question (task outputs must not leak between questions)."""
    kb_agent = create_knowledge_agent()
    web_agent = create_web_search_agent()
    log_agent = create_logger_agent()

    for a in (kb_agent, web_agent, log_agent):
        a.verbose = VERBOSE

    kb_task = create_knowledge_task(kb_agent)
    web_task = create_web_search_task(web_agent, kb_task)
    log_task = create_logging_task(log_agent, kb_task, web_task)

    crew = Crew(
        agents=[kb_agent, web_agent, log_agent],
        tasks=[kb_task, web_task, log_task],
        process=Process.sequential,
        verbose=VERBOSE,
    )
    return crew, kb_task, web_task, log_task


def answer_question(question: str) -> dict:
    crew, kb_task, web_task, log_task = build_crew()
    crew.kickoff(inputs={"question": question})

    kb = kb_task.output.pydantic
    web_ran = web_task.output is not None and web_task.output.raw != ""

    if web_ran:
        web = web_task.output.pydantic
        result = {
            "answered_by": "Web Search (Agent 2)",
            "answer": f"{web.answer}\n\nNote: {web.disclaimer}",
            "sources": web.sources,
        }
    else:
        result = {
            "answered_by": "Knowledge Base (Agent 1)",
            "answer": kb.answer,
            "sources": kb.sources,
        }
    result["confidence"] = kb.confidence
    result["log_status"] = log_task.output.raw if log_task.output else "not logged"
    return result


def print_result(question: str, r: dict):
    print("\n" + "=" * 70)
    print(f"Q: {question}")
    print(f"[{r['answered_by']} | KB confidence {r['confidence']:.3f}]\n")
    print(r["answer"])
    if r["sources"]:
        print("\nSources:")
        for s in r["sources"]:
            print(f"  - {s}")
    print(f"\n({r['log_status']})")
    print("=" * 70 + "\n")


def chat():
    print("NovaWave Support Assistant - ask about HR, leave, IT, policies. Type 'exit' to quit.\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            continue
        if q.lower() in {"exit", "quit", "bye"}:
            break
        print_result(q, answer_question(q))
    print("Goodbye!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print_result(q, answer_question(q))
    else:
        chat()
