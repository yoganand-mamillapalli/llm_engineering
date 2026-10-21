from __future__ import annotations

import asyncio

from langchain.agents import create_agent
from langchain_core.tools import tool

try:
    from llm_engineering.llm_provider import create_model
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model

TEAM_CONTEXT = {
    "product": "Product launch is scheduled for Nov 20. The release requires customer onboarding support and bug triage.",
    "support": "Support can answer billing and access questions, but they must escalate product bugs to engineering.",
    "engineering": "Engineering owns technical defects, rollout risk, and system availability. They do not decide billing policy.",
    "policy": "If a question touches money, policy, or account access, support should answer from policy first before escalating.",
}

conversation_history: list[str] = []


@tool
def get_team_context(topic: str) -> str:
    """Return the relevant team context for a question or decision."""
    query = topic.strip().lower()
    matches: list[str] = []
    for key, value in TEAM_CONTEXT.items():
        if query in key.lower() or query in value.lower():
            matches.append(value)

    if not matches:
        return "No matching team context found."
    return "\n".join(matches)


@tool
def remember_decision(note: str) -> str:
    """Save a team decision in the current session so future steps can reuse it."""
    note = note.strip()
    if not note:
        return "No decision recorded."
    conversation_history.append(note)
    return f"Recorded: {note}"


def last_message_text(result: dict) -> str:
    messages = result.get("messages", [])
    if not messages:
        return "No message returned."
    content = messages[-1].content
    return content if isinstance(content, str) else str(content)


def build_agent(name: str, role: str, tools: list):
    return create_agent(
        model=create_model(),
        tools=tools,
        system_prompt=(
            f"You are the {name} agent. {role}. "
            "Use the latest team context and only answer from known facts. "
            "If facts are missing, say what is missing instead of guessing."
        ),
    )


async def run_team_question(question: str) -> str:
    previous_context = "\n".join(conversation_history[-3:]) or "No previous team notes yet."

    coordinator = build_agent(
        "Coordinator",
        "Break the task into specialist responsibilities and make sure each team answers only its lane.",
        [get_team_context, remember_decision],
    )
    coordinator_result = await coordinator.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"Recent team notes:\n{previous_context}\n"
                        "Identify the relevant roles and decide which teams should answer."
                    ),
                }
            ]
        }
    )
    coordinator_summary = last_message_text(coordinator_result)

    support_agent = build_agent(
        "Support",
        "Answer customer-facing policy and access questions; do not speculate on engineering issues.",
        [get_team_context],
    )
    engineering_agent = build_agent(
        "Engineering",
        "Flag technical risk, rollout constraints, or implementation concerns only when the question is technical.",
        [get_team_context],
    )
    support_input = {
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Coordinator summary:\n{coordinator_summary}\n"
                    "Answer only from the support context and explain any required escalation."
                ),
            }
        ]
    }
    engineering_input = {
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Coordinator summary:\n{coordinator_summary}\n"
                    "State only engineering concerns or constraints that are clearly supported by the context."
                ),
            }
        ]
    }
    support_result, engineering_result = await asyncio.gather(
        support_agent.ainvoke(support_input),
        engineering_agent.ainvoke(engineering_input),
    )
    support_answer = last_message_text(support_result)
    engineering_answer = last_message_text(engineering_result)

    final_agent = build_agent(
        "Final Decision",
        "Combine the support and engineering inputs into one final team answer. Keep context-grounded reasoning and state any uncertainty clearly.",
        [get_team_context],
    )
    final_result = await final_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Support answer:\n{support_answer}\n\n"
                        f"Engineering answer:\n{engineering_answer}\n\n"
                        f"Team context summary:\n{coordinator_summary}"
                    ),
                }
            ]
        }
    )
    return last_message_text(final_result)


async def main() -> None:
    print("Context-aware team-of-agents demo")
    print("Type 'quit' to exit.\n")

    while True:
        question = input("Ask a product, support, or engineering question: ").strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break

        remember_decision.invoke({"note": f"Current question: {question}"})
        response = await run_team_question(question)
        print(f"\n{response}\n")


if __name__ == "__main__":
    asyncio.run(main())
