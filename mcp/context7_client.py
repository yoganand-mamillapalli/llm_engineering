import asyncio
import os

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


CONTEXT7_URL = "https://mcp.context7.com/mcp"


async def main() -> None:
    library_name = input("Library name (for example, FastAPI): ").strip()
    question = input("What do you want to know? ").strip()
    if not library_name or not question:
        print("Enter both a library name and a question.")
        return

    headers = {}
    api_key = os.getenv("CONTEXT7_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    async with httpx.AsyncClient(headers=headers) as http_client:
        async with streamable_http_client(
            CONTEXT7_URL,
            http_client=http_client,
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                print("Context7 tools:")
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")

                matches = await session.call_tool(
                    "resolve-library-id",
                    {"libraryName": library_name, "query": question},
                )
                print("\nMatching library IDs:")
                for item in matches.content:
                    if hasattr(item, "text"):
                        print(item.text)

                library_id = input("Paste the library ID to use: ").strip()
                if not library_id:
                    return

                docs = await session.call_tool(
                    "query-docs",
                    {"libraryId": library_id, "query": question},
                )
                print("\nDocumentation:")
                for item in docs.content:
                    if hasattr(item, "text"):
                        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())