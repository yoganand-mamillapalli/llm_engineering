# AI Learning Reference

Small Python examples for learning LLM calls, tools, agents, and hooks.
The examples are intended as a simple reference for developers starting with
LLM application code.

Example: when asked for the weather and local time in New York, the model can
choose the matching Python helpers, which run and return the results.

## Topics covered

- Selecting Google Gemini, OpenRouter, or Groq from `.env`.
- Using LangChain for a common model and agent interface.
- Letting the model select weather and timezone tools.
- Calling multiple tools for one question.
- Validating model responses against a Pydantic schema.
- Adding a LangChain middleware hook for agent progress.
- Using a reusable skill to guide an answer.
- Combining a skill with weather and timezone tools.
- Combining a skill with Python documentation through Context7 MCP.
- Comparing fixed multi-agent workflows, team workflows, and supervisor/subagent delegation.
- Using web search and library documentation to design a solution from a problem statement.
- Comparing LangChain with direct provider SDKs.
- Connecting to tools through a separate MCP server process.

## Run examples

Run these commands from the workspace root:

```powershell
python -m pip install -r llm_engineering/requirements.txt
Copy-Item llm_engineering/.env.example llm_engineering/.env
python -m llm_engineering.langchain_demo
python -m llm_engineering.structured_outputs.demo
python -m llm_engineering.tools.tool_demo
python -m llm_engineering.hooks.logging_hook_demo
python -m llm_engineering.skills.skill_demo
python -m llm_engineering.skills.weather_timezone_demo
python -m llm_engineering.skills.problem_solver_demo
python -m llm_engineering.agents.multi_agent_context_demo
python -m llm_engineering.agents.team_agents_demo
python -m llm_engineering.agents.subagent_demo
python -m llm_engineering.mcp.client
python -m llm_engineering.mcp.context7_client
python -m unittest discover -s llm_engineering/structured_outputs/tests -v
```

In VS Code, select the workspace `.venv` with **Python: Select Interpreter**.
Open **Run and Debug** and choose an `LLM:` configuration to run a demo as a
module from the workspace root. This keeps package imports consistent whether
you run from the terminal or debugger.
Agent Run and Debug profiles are available for the multi-agent context, team
agents, and subagent demos.

You can also open this `llm_engineering` directory itself as a VS Code folder.
Its `.vscode` settings select the parent workspace's `.venv`, and its launch
profiles run modules with the parent directory as the working directory. When
using the integrated terminal, move to the parent directory before running the
commands above: `Set-Location ..`.

Select one provider in `.env`:

```env
LLM_PROVIDER=google
```

or:

```env
LLM_PROVIDER=openrouter
```

or:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
```

Set `GROQ_MODEL` in `.env` to override the default Groq model.

## Project structure

- `langchain_demo.py` sends one normal question through LangChain.
- `llm_provider.py` creates the selected Google, OpenRouter, or Groq model through the shared LangChain interface.
- `structured_outputs/` contains the support-ticket structured-output demo, its README, and offline parser tests.
- `tools/` contains LangChain and direct SDK tool examples.
- `hooks/` contains a basic LangChain middleware example.
- `skills/` contains reusable instructions and demos combining skills with tools, web search, and Context7 MCP.
- `agents/` compares context-aware stages, an explicitly orchestrated team, and a supervisor that delegates to subagents. See its README for the learning guide.
- `mcp/` contains a local stdio notes server and a remote Context7 HTTP client.
- `plan.md` contains the learning sequence and exercises.

## Important implementation notes

Google and OpenRouter do not define tools in the same way. The direct examples
show those differences. The main LangChain example keeps the tool functions
the same for both providers.

The context-aware agent demo keeps conversation notes in process memory and
searches those notes with simple substring matching; restarting the process
clears them. The team demo passes its latest three notes to the coordinator.
Neither example persists conversation memory between runs.

Google automatic function calling uses `chats.create()` and `send_message()`.
API keys stay in `.env` and are not placed in Python files.
