from pathlib import Path

from langchain.agents import create_agent

try:
    from llm_engineering.llm_provider import create_model
    from llm_engineering.tools.tool_demo import get_timezone, get_weather
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model
    from tools.tool_demo import get_timezone, get_weather


SKILL_PATH = Path(__file__).resolve().parent / "weather_timezone" / "SKILL.md"


def main() -> None:
    skill_instructions = SKILL_PATH.read_text(encoding="utf-8")
    agent = create_agent(
        model=create_model(),
        tools=[get_weather, get_timezone],
        system_prompt=skill_instructions,
    )
    while True:
        city = input("Enter a city (or 'quit' to exit): ").strip()
        if city.lower() in {"quit", "exit"}:
            break
        if not city:
            continue

        question = f"Get both the weather and timezone for {city}."
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )
        print(f"\n{city}:")
        answer = result["messages"][-1].content
        print(answer if isinstance(answer, str) else str(answer))


if __name__ == "__main__":
    main()