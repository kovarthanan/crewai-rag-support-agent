"""Task definitions: knowledge task, conditional web search task, logging task."""

from crewai import Agent, Task
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput

from models import KnowledgeBaseAnswer, WebSearchAnswer


def create_knowledge_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Employee question: {question}\n\n"
            "1. Use the `company_policy_search` tool to find relevant passages. "
            "You may search again with a rephrased query if the first results are weak.\n"
            "2. Answer ONLY from the returned passages. Do not use outside knowledge.\n"
            "3. Set is_satisfied = true ONLY if:\n"
            "   - the tool reports CONFIDENCE: HIGH, AND\n"
            "   - the passages directly and completely answer the question.\n"
            "   Otherwise set is_satisfied = false and say what is missing.\n"
            "4. Set confidence to the BEST_SCORE reported by the tool.\n"
            "5. List the sources as 'file > section'."
        ),
        expected_output=(
            "A KnowledgeBaseAnswer with a clear answer, is_satisfied flag, "
            "confidence score, sources and a one-line reason."
        ),
        agent=agent,
        output_pydantic=KnowledgeBaseAnswer,
    )


# ------------------------------------------------------------------ routing
def needs_web_search(output: TaskOutput) -> bool:
    """Condition for Agent 2: run only when Agent 1 was NOT satisfied."""
    kb: KnowledgeBaseAnswer | None = output.pydantic
    if kb is None:            # Agent 1 output could not be parsed -> be safe, search the web
        return True
    return not kb.is_satisfied


def create_web_search_task(agent: Agent, knowledge_task: Task) -> ConditionalTask:
    return ConditionalTask(
        description=(
            "Employee question: {question}\n\n"
            "The company knowledge base could NOT answer this question satisfactorily "
            "(see the previous result in your context for what was missing).\n\n"
            "1. Use the search tool to find the answer on the public web. "
            "Try a refined query if the first results are weak.\n"
            "2. Prefer official / authoritative sources (e.g. .gov.in, epfindia.gov.in, "
            "incometax.gov.in, official company sites).\n"
            "3. Write a concise answer (max ~120 words) using only what the sources say.\n"
            "4. List the URLs you used in `sources`.\n"
            "5. If nothing reliable is found, set found = false and say so honestly.\n"
            "6. Add a one-line disclaimer that this is from the public web, "
            "not NovaWave company policy."
        ),
        expected_output="A WebSearchAnswer with answer, source URLs, found flag and disclaimer.",
        agent=agent,
        context=[knowledge_task],
        condition=needs_web_search,
        output_pydantic=WebSearchAnswer,
    )


# ------------------------------------------------------------------ logging
def create_logging_task(agent: Agent, knowledge_task: Task, web_task: Task) -> Task:
    return Task(
        description=(
            "Employee question: {question}\n\n"
            "Your context contains the result of the Knowledge Base agent and, ONLY if it ran, "
            "the result of the Web Search agent.\n\n"
            "Decide the FINAL answer:\n"
            "- If a Web Search result is present in your context, the final answer is the "
            "web search answer -> answered_by = 'Web Search (Agent 2)'; sources = its URLs; "
            "status = RESOLVED if found is true, else UNRESOLVED.\n"
            "- Otherwise the final answer is the Knowledge Base answer -> "
            "answered_by = 'Knowledge Base (Agent 1)'; sources = its document sections; "
            "status = RESOLVED.\n"
            "- confidence = the Knowledge Base 'confidence' value in both cases.\n\n"
            "Call the `support_log_writer` tool exactly ONCE with these fields. "
            "Copy the answer text exactly - do not summarise or change it."
        ),
        expected_output="Confirmation message returned by the support_log_writer tool.",
        agent=agent,
        context=[knowledge_task, web_task],   # a skipped web task is automatically left out
    )
