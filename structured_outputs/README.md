# Structured Outputs: Support Ticket Triage

This example asks an LLM to classify a support ticket and return a response
matching a Pydantic schema. The allowed category and priority values are
validated locally by LangChain's `PydanticOutputParser`.

Run from the workspace root after configuring a provider in
`llm_engineering/.env`:

```powershell
python -m llm_engineering.structured_outputs.demo
```

Try a ticket such as:

```text
I was charged twice for my monthly subscription. Please help me understand the extra charge.
```

The parser checks the response's structure and allowed values; it cannot tell
whether the model chose the correct category or priority.

## Tests

The tests use a fake model response, so they do not require an API key or make
network calls. Run them from the workspace root:

```powershell
python -m unittest discover -s llm_engineering/structured_outputs/tests -v
```