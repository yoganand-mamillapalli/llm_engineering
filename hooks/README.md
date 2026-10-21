# Agent Hooks

This folder contains a small LangChain middleware example.
Hooks are checkpoints that run at key moments, such as before a model call or
while a tool runs. This example uses them to keep a short activity log.

`logging_hook_demo.py` uses three middleware hooks:

- `before_model` logs the request ID, context message count, and message types.
- `wrap_model_call` measures model duration and logs model failures.
- `wrap_tool_call` logs the tool name, argument names, duration, and failures.

The actual prompt and argument values are not logged, which avoids putting
private text in the log.

Run from the workspace root:

```powershell
python -m llm_engineering.hooks.logging_hook_demo
```

This is a starting point for hooks that add input checking, retries, cost
tracking, and approval before a tool is called.
