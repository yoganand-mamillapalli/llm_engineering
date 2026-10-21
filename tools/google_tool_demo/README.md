# Google Direct Tool Example

This folder uses the Google GenAI SDK directly. It contains weather and
timezone functions.

Google can understand the tools from the function name, type annotation, and
docstring. The functions are passed directly in the request:

In other words, the function's name, inputs, and description tell Google what
the helper does and how to call it.

```python
config={"tools": [get_weather, get_timezone]}
```

The code uses `client.chats.create()` and `send_message()` for automatic
function calling.

Run from the `llm_engineering` folder:

```powershell
Copy-Item tools/google_tool_demo/.env.example tools/google_tool_demo/.env
python tools/google_tool_demo/tool_demo.py
```

The key is in the local `.env` file. This file is ignored by Git.

Using `models.generate_content()` with automatic function calling produced an
AFC warning. The chat method is the recommended approach and removes that
warning.
