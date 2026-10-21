# Tool Calling

These examples show how an LLM can select and run Python functions.
Think of tools as helpers the model can ask the application to run.

The main file is `tool_demo.py`. It has two tools:

- `get_weather(city)`
- `get_timezone(city)`

They are normal Python functions with the LangChain `@tool` decorator. The
agent decides which tool is needed. If the question asks for both, the agent
can call both tools.

Run from the workspace root:

```powershell
python -m llm_engineering.tools.tool_demo
```

Example question:

```text
What is the weather and timezone in New York?
```

The other folders show the same idea without LangChain. They make the
differences between Google and OpenRouter visible.

## Important concept

A tool is not only a function name. The model also needs the function meaning
and its parameters. Google can infer this from a typed function and docstring.
OpenRouter needs an explicit JSON schema.
