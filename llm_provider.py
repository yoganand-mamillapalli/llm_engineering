import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def create_model(model: str | None = None):
    provider = os.getenv("LLM_PROVIDER", "google").strip().lower()

    if provider == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")
        return ChatGoogleGenerativeAI(
            model=model or os.getenv("GOOGLE_MODEL", "gemini-3.8-flash"),
            google_api_key=api_key,
            temperature=0,
        )

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing. Add it to your .env file.")
        return ChatOpenAI(
            model=model or os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
        )

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")
        return ChatGroq(
            model=model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            api_key=api_key,
            temperature=0,
        )

    raise ValueError("LLM_PROVIDER must be 'google', 'openrouter', or 'groq'.")
