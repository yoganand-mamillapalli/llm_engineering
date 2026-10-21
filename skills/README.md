# Skills

A skill is reusable guidance that tells a model how to handle a kind of task.
For example, this skill asks the model to explain beginner Python clearly.

A tool performs an action or returns data. A skill guides the model's approach;
it does not run code by itself. A skill can tell a model when to use tools, but
this small example uses instructions only.

`skill_demo.py` reads `python_basics/SKILL.md` and sends it as the system
message, separate from the user's question. This is a simple way to see the
idea; a regular system prompt could contain the same instructions inline.

Run from the workspace root:

```powershell
python -m llm_engineering.skills.skill_demo
```

Try asking: `What is a Python list?`

## Skill With Tools

`weather_timezone_demo.py` combines a skill with the existing weather and
timezone tools. The skill guides the answer; the tools provide sample data.
For each city, the agent calls both tools and prints both results. Enter
another city to continue, or type `quit` to exit.

```powershell
python -m llm_engineering.skills.weather_timezone_demo
```

Try entering: `Paris`

## Problem Solving With MCP

`problem_solver_demo.py` accepts a plain-language problem. Its skill guides the
analysis, Tavily searches for current approaches, and Context7 checks Python
library documentation when relevant. It proposes a design; it does not change
files or execute code.

Run from the workspace root:

```powershell
python -m llm_engineering.skills.problem_solver_demo
```

The model provider key is required. Tavily uses free keyless MCP access by
default; `TAVILY_API_KEY` is optional. `CONTEXT7_API_KEY` is also optional.