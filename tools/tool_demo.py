from langchain.agents import create_agent
from langchain_core.tools import tool

try:
    from llm_engineering.llm_provider import create_model
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    weather_map = {
        "paris": "Sunny, 24C",
        "london": "Cloudy, 18C",
        "new york": "Rainy, 21C",
    }
    return weather_map.get(city.lower(), f"No weather data for {city}")


@tool
def get_timezone(city: str) -> str:
    """Get the timezone for a city."""
    timezone_map = {
        "paris": "Europe/Paris",
        "london": "Europe/London",
        "new york": "America/New_York",
    }
    return timezone_map.get(city.lower(), f"No timezone data for {city}")


def ask_llm_with_tools(question: str) -> str:
    agent = create_agent(
        model=create_model(),
        tools=[get_weather, get_timezone],
        system_prompt=(
            "Use every relevant tool to answer completely. "
            "If the user asks for both weather and timezone, use both tools."
        ),
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    answer = result["messages"][-1].content
    return answer if isinstance(answer, str) else str(answer)


if __name__ == "__main__":
    question = input("Ask about weather or timezone: ").strip()
    print(ask_llm_with_tools(question))
