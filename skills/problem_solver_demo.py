import asyncio
import os
from contextlib import AsyncExitStack
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult

try:
    from llm_engineering.llm_provider import create_model
    from llm_engineering.mcp.context7_client import CONTEXT7_URL
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model
    from mcp.context7_client import CONTEXT7_URL


TAVILY_URL = "https://mcp.tavily.com/mcp/"
SKILL_PATH = Path(__file__).resolve().parent / "problem_solving" / "SKILL.md"
load_dotenv(PROJECT_ROOT / ".env")


def result_text(result: CallToolResult) -> str:
    text = "\n".join(
        item.text for item in result.content if hasattr(item, "text")
    )
    if text:
        return text
    if result.structuredContent is not None:
        return str(result.structuredContent)
    return "The MCP server returned no content."


async def main() -> None:
    problem = input("Describe the problem you want to solve: ").strip()
    if not problem:
        print("Enter a problem statement to continue.")
        return

    tavily_key = os.getenv("TAVILY_API_KEY")
    tavily_headers = (
        {"Authorization": f"Bearer {tavily_key}"}
        if tavily_key
        else {"X-Tavily-Access-Mode": "keyless"}
    )
    context7_key = os.getenv("CONTEXT7_API_KEY")
    context7_headers = (
        {"Authorization": f"Bearer {context7_key}"} if context7_key else {}
    )

    async with AsyncExitStack() as stack:
        tavily_http = await stack.enter_async_context(
            httpx.AsyncClient(headers=tavily_headers)
        )
        tavily_read, tavily_write, _ = await stack.enter_async_context(
            streamable_http_client(TAVILY_URL, http_client=tavily_http)
        )
        tavily_session = await stack.enter_async_context(
            ClientSession(tavily_read, tavily_write)
        )
        await tavily_session.initialize()

        context7_http = await stack.enter_async_context(
            httpx.AsyncClient(headers=context7_headers)
        )
        context7_read, context7_write, _ = await stack.enter_async_context(
            streamable_http_client(CONTEXT7_URL, http_client=context7_http)
        )
        context7_session = await stack.enter_async_context(
            ClientSession(context7_read, context7_write)
        )
        await context7_session.initialize()

        @tool
        async def web_search(query: str) -> str:
            """Search the web for current approaches and evidence."""
            result = await tavily_session.call_tool(
                "tavily_search", {"query": query, "max_results": 5}
            )
            return result_text(result)

        @tool
        async def resolve_library_id(library_name: str, query: str) -> str:
            """Find Context7 IDs for a library before looking up its docs."""
            result = await context7_session.call_tool(
                "resolve-library-id",
                {"libraryName": library_name, "query": query},
            )
            return result_text(result)

        @tool
        async def query_library_docs(library_id: str, query: str) -> str:
            """Fetch current documentation for an exact Context7 library ID."""
            result = await context7_session.call_tool(
                "query-docs",
                {"libraryId": library_id, "query": query},
            )
            return result_text(result)

        skill_instructions = SKILL_PATH.read_text(encoding="utf-8")
        agent = create_agent(
            model=create_model(),
            tools=[web_search, resolve_library_id, query_library_docs],
            system_prompt=skill_instructions,
        )
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": problem}]}
        )
        used_tools = [
            call["name"]
            for message in response["messages"]
            for call in getattr(message, "tool_calls", [])
        ]
        print("Research tools used:", ", ".join(used_tools) or "none")
        answer = response["messages"][-1].content
        print(answer if isinstance(answer, str) else str(answer))


if __name__ == "__main__":
    asyncio.run(main())