from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

try:
    from llm_engineering.llm_provider import create_model
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model


SKILL_PATH = Path(__file__).resolve().parent / "python_basics" / "SKILL.md"


def main() -> None:
    skill_instructions = SKILL_PATH.read_text(encoding="utf-8")
    question = input("Ask a beginner Python question: ").strip()
    if not question:
        question = "What is a Python list?"

    response = create_model().invoke(
        [
            SystemMessage(content=skill_instructions),
            HumanMessage(content=question),
        ]
    )
    print(response.content)


if __name__ == "__main__":
    main()