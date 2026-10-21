try:
    from llm_engineering.llm_provider import create_model
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model


question = input("Ask a question: ").strip() or "What is artificial intelligence?"
response = create_model().invoke(question)
print(response.content)
