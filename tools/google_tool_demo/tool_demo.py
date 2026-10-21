import os

from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def get_weather(city: str) -> str:
    """Get the weather for a city."""
    weather_map = {
        "paris": "Sunny, 24C",
        "london": "Cloudy, 18C",
        "new york": "Rainy, 21C",
    }
    return weather_map.get(city.lower(), f"No weather data for {city}")


def get_timezone(city: str) -> str:
    """Get the timezone for a city."""
    timezone_map = {
        "paris": "Europe/Paris",
        "london": "Europe/London",
        "new york": "America/New_York",
    }
    return timezone_map.get(city.lower(), f"No timezone data for {city}")


def ask_google(question: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Add it to google_tool_demo/.env.")

    client = genai.Client(api_key=api_key)
    
    chat = client.chats.create(
        model=os.getenv("GOOGLE_MODEL", "gemini-3.8-flash"),
        config={
            "tools": [get_weather, get_timezone],
            "system_instruction": (
                "Use every relevant tool. If the user asks for both weather and timezone, "
                "call both tools."
            ),
        },
    )
    response = chat.send_message(question)
    return response.text or ""


if __name__ == "__main__":
    question = input("Ask about weather or timezone: ").strip()
    print(ask_google(question))
