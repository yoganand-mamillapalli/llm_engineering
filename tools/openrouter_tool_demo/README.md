# OpenRouter Direct Tool Example

This folder uses OpenRouter directly with the OpenAI-compatible Python client.
It contains the same weather and timezone functions as the Google example.

The tool JSON schema is written manually. OpenRouter does not inspect the
Python function to create the schema. The model returns a tool call and the
Python code runs the matching function.

Think of the schema as a form that tells the model which helper it can request
and what information that helper needs.

Run from the `llm_engineering` folder:

```powershell
Copy-Item tools/openrouter_tool_demo/.env.example tools/openrouter_tool_demo/.env
python tools/openrouter_tool_demo/tool_demo.py
```

The key is in the local `.env` file. This file is ignored by Git.

This example contains more code than the LangChain example, but makes the
provider protocol easier to understand.
