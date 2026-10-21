import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def get_weather(city: str) -> str:
    weather_map = {
        "paris": "Sunny, 24C",
        "london": "Cloudy, 18C",
        "new york": "Rainy, 21C",
    }
    return weather_map.get(city.lower(), f"No weather data for {city}")


def get_timezone(city: str) -> str:
    timezone_map = {
        "paris": "Europe/Paris",
        "london": "Europe/London",
        "new york": "America/New_York",
    }
    return timezone_map.get(city.lower(), f"No timezone data for {city}")


def ask_openrouter(question: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing. Add it to openrouter_tool_demo/.env.")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a city.",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timezone",
                "description": "Get timezone for a city.",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        },
    ]

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        messages=[
            {
                "role": "system",
                "content": (
                    "Use  relevant tool. If the user asks for both weather and timezone, "
                    "call both tools."
                ),
            },
            {"role": "user", "content": question},
        ],
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=True,
    )

    message = response.choices[0].message
    if message.tool_calls:
        answers = []
        for call in message.tool_calls:
            city = json.loads(call.function.arguments)["city"]
            if call.function.name == "get_weather":
                answers.append(f"Weather: {get_weather(city)}")
            elif call.function.name == "get_timezone":
                answers.append(f"Timezone: {get_timezone(city)}")
        return "\n".join(answers)
    return message.content or ""


if __name__ == "__main__":
    question = input("Ask about weather or timezone: ").strip()
    print(ask_openrouter(question))
