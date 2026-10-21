from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.tools import tool

try:
    from llm_engineering.llm_provider import create_model
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model

CONTEXT_MEMORY = {
    "migration": "The Acme CRM migration is scheduled for November 15. Legacy access stays available until November 20.",
    "support_policy": "Support policy: during a migration, customers may keep temporary access to the legacy dashboard until the cutover is complete.",
    "prior_turn": "Customer previously asked about access during the migration window and wanted the final timeline.",
}

conversation_history: list[str] = []


@tool
def get_project_context(topic: str) -> str:
    """Return matching project context and notes saved earlier in this session."""
    query = topic.strip().lower()
    matches: list[str] = []
    for key, value in CONTEXT_MEMORY.items():
        if query in key.lower() or query in value.lower():
            matches.append(value)
    for note in conversation_history:
        if query in note.lower():
            matches.append(f"Saved conversation note: {note}")

    if not matches:
        return "No matching project context found."
    return "\n".join(matches)


@tool
def remember_context(note: str) -> str:
    """Save a fact from the current conversation so later turns can reuse it."""
    note = note.strip()
    if not note:
        return "No note saved."
    conversation_history.append(note)
    return f"Saved context: {note}"


def last_message_text(result: dict) -> str:
    messages = result.get("messages", [])
    if not messages:
        return "No message returned."
    content = messages[-1].content
    return content if isinstance(content, str) else str(content)


def build_agent(name: str, instructions: str, tools: list):
    return create_agent(
        model=create_model(),
        tools=tools,
        system_prompt=(
            f"You are the {name} agent. "
            f"{instructions} "
            "Use the provided context before guessing. If facts are missing, say so clearly."
        ),
    )


def answer_with_context(question: str) -> str:
    previous_context = "\n".join(conversation_history) or "No previous context from this session yet."

    context_agent = build_agent(
        "context specialist",
        "Extract only the facts relevant to the user question and ignore unrelated project details.",
        [get_project_context, remember_context],
    )
    context_result = context_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"User question: {question}\n"
                        f"Recent conversation context:\n{previous_context}\n"
                        "Find the most relevant facts and keep only those you will use."
                    ),
                }
            ]
        }
    )
    relevant_facts = last_message_text(context_result)

    answer_agent = build_agent(
        "answer specialist",
        "Answer using only the relevant facts. If the answer depends on missing context, say that explicitly.",
        [get_project_context],
    )
    answer_result = answer_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"Relevant facts:\n{relevant_facts}"
                    ),
                }
            ]
        }
    )
    answer = last_message_text(answer_result)

    reviewer_agent = build_agent(
        "reviewer",
        "Check whether the answer is grounded in the provided context and whether it explains any missing facts.",
        [get_project_context],
    )
    review_result = reviewer_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"Candidate answer:\n{answer}\n\n"
                        f"Relevant facts:\n{relevant_facts}"
                    ),
                }
            ]
        }
    )
    return last_message_text(review_result)


def main() -> None:
    print("Context-aware multi-agent demo")
    print("Type 'quit' to exit.\n")

    while True:
        question = input("Ask about the project or migration timeline: ").strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break

        remember_context.invoke({"note": f"User asked: {question}"})
        reply = answer_with_context(question)
        print(f"\n{reply}\n")


if __name__ == "__main__":
    main()
