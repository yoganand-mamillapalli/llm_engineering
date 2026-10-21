from mcp.server.fastmcp import FastMCP


mcp = FastMCP("notes-server")
notes: list[str] = []


@mcp.tool()
def add_note(text: str) -> str:
    """Save a short note in memory."""
    notes.append(text)
    return f"Saved note: {text}"


@mcp.tool()
def search_notes(keyword: str) -> list[str]:
    """Find saved notes containing a keyword."""
    return [note for note in notes if keyword.lower() in note.lower()]


if __name__ == "__main__":
    mcp.run()
