# MCP Server and Client

This folder is a small MCP example with a notes topic.

- MCP (Model Context Protocol) is a bit like USB for AI applications: it gives
	clients and external services a standard way to connect and communicate,
	instead of requiring a custom integration for every pair. The comparison is
	about interoperability, not hardware: MCP is a protocol, not a cable, and it
	can describe tools and other context, not just tool calls.
- Everyday example: imagine asking an AI assistant, "What meetings do I have
	tomorrow?" The calendar can offer an MCP server, and the assistant can use
	the same standard way to discover and request calendar information. Without
	a shared standard, each assistant and calendar would need its own connector.
- In this demo, the notes server plays the role of the calendar: the client
	discovers `add_note` and `search_notes`, then calls them through MCP.
- `server.py` exposes `add_note` and `search_notes` tools.
- `client.py` starts the server as a separate process.
- The client discovers the tools and calls them through MCP.
- Notes are stored only in memory for this learning example.

Run from the workspace root:

```powershell
python -m llm_engineering.mcp.client
```

The important idea is the process boundary:

```text
AI application (MCP client) -> MCP protocol -> MCP server -> Python tool
```

In this example, the client launches the server as a separate process and
communicates with it over standard input/output. The protocol provides the
shared language for discovering and calling the server's tools. This differs
from a normal LangChain tool, where the function normally runs inside the same
application process.

## Connect to Context7

`context7_client.py` connects to Context7's hosted server over Streamable HTTP.
Unlike the notes example, it does not start a local server. It asks for a
library and question, shows matching library IDs, then fetches documentation
for the ID you choose.

Run from the workspace root:

```powershell
python -m llm_engineering.mcp.context7_client
```

Context7 works without an API key for basic use. Set `CONTEXT7_API_KEY` in the
environment for higher rate limits.
