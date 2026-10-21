import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult


def get_tool_result(result: CallToolResult) -> object:
    if result.structuredContent is not None:
        return result.structuredContent
    return [item.text for item in result.content if hasattr(item, "text")]


async def main() -> None:
    workspace_root = Path(__file__).resolve().parents[1]
    try:
        __import__("llm_engineering.mcp.server")
        server_module = "llm_engineering.mcp.server"
    except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
        server_module = "mcp.server"
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module],
        cwd=str(workspace_root),
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools exposed by MCP server:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            saved = await session.call_tool(
                "add_note",
                {"text": "Learn MCP server and client communication."},
            )
            print("Add result:", get_tool_result(saved))

            found = await session.call_tool("search_notes", {"keyword": "MCP"})
            print("Search match:", get_tool_result(found))

            missing = await session.call_tool(
                "search_notes", {"keyword": "no-such-note"}
            )
            print("Search with no match:", get_tool_result(missing))


if __name__ == "__main__":
    asyncio.run(main())
