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
DEFAULT_QUESTION = (
    "A customer reports a login bug and asks an account-access question. "
    "What should support handle, and what should engineering investigate?"
)


@tool
def get_team_context(topic: str) -> str:
    """Return team facts matching the requested topic."""
    query = topic.strip().lower()
    matches = [
        value
        for key, value in TEAM_CONTEXT.items()
        if query in key.lower() or query in value.lower()
    ]
    if not matches:
        return "No matching team context found."
    return "\n".join(matches)


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
            f"You are the {name} agent. {instructions} "
            "Use only known team facts; explain when information is missing."
        ),
    )


async def answer_with_subagents(question: str) -> str:
    support_agent = build_agent(
        "Support subagent",
        "Handle customer-facing policy, billing, and account access questions. "
        "Escalate product bugs to engineering.",
        [get_team_context],
    )
    engineering_agent = build_agent(
        "Engineering subagent",
        "Handle technical defects, rollout risk, and system availability. "
        "Do not decide billing policy.",
        [get_team_context],
    )

    @tool
    async def ask_support_subagent(task: str) -> str:
        """Delegate a customer policy, billing, or account access task to support."""
        result = await support_agent.ainvoke(
            {"messages": [{"role": "user", "content": task}]}
        )
        return last_message_text(result)

    @tool
    async def ask_engineering_subagent(task: str) -> str:
        """Delegate a technical defect, rollout, or availability task to engineering."""
        result = await engineering_agent.ainvoke(
            {"messages": [{"role": "user", "content": task}]}
        )
        return last_message_text(result)

    supervisor = build_agent(
        "Supervisor",
        "Answer the user by delegating relevant work to the support and/or engineering "
        "subagents. Choose only the specialist tools needed for the question, then "
        "synthesize their results. Do not answer from assumptions.",
        [ask_support_subagent, ask_engineering_subagent],
    )
    result = await supervisor.ainvoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    return last_message_text(result)


async def main() -> None:
    print("Supervisor and subagents demo")
    print("Type 'quit' to exit.\n")

    while True:
        question = input(
            "Ask a product, policy, or engineering question.\n"
            f"Press Enter to try: {DEFAULT_QUESTION}\n> "
        ).strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            question = DEFAULT_QUESTION

        answer = await answer_with_subagents(question)
        print(f"\nQuestion: {question}\nAnswer: {answer}\n")
        input("Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
