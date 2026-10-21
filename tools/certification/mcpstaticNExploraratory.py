import asyncio
import json
from fastmcp import FastMCP, Client

# ==========================================
# 1. MCP SERVER DEFINITION
# ==========================================
mcp = FastMCP("CatalogServer")

DATABASE = {
    "movies": [
        {"id": "m1", "title": "Inception", "genre": "Sci-Fi"},
        {"id": "m2", "title": "The Matrix", "genre": "Sci-Fi"}
    ],
    "books": [
        {"id": "b1", "title": "Dune", "author": "Frank Herbert"}
    ]
}

@mcp.resource("catalog://root/summary")
def get_root_summary() -> str:
    """Connection-time static summary of catalogs."""
    return json.dumps({
        "categories": list(DATABASE.keys()),
        "template": "catalog://{category}/{item_id}"
    }, indent=2)

@mcp.resource("catalog://{category}/{item_id}")
def get_catalog_item(category: str, item_id: str) -> str:
    """Exploratory-time dynamic resource template."""
    if category not in DATABASE:
        return json.dumps({"error": f"Category '{category}' not found."})
    item = next((i for i in DATABASE[category] if i["id"] == item_id), None)
    if not item:
        return json.dumps({"error": f"Item '{item_id}' not found."})
    return json.dumps(item, indent=2)


# ==========================================
# 2. AGENT (CLIENT) CODE & EXECUTION
# ==========================================
async def main():
    # Bind the client directly to the server in-memory for a single script
    client = Client(mcp)
    
    async with client:
        print("=== CONNECTION TIME ===")
        resources = await client.list_resources()
        for res in resources:
            print(f"- Discovered: {res.uri} ({res.name})")
            
        print("\n=== EXPLORATORY TIME ===")
        target_uri = "catalog://movies/m1"
        print(f"Agent exploring: {target_uri}")
        
        response = await client.read_resource(target_uri)
        for content in response:
            print("Payload received by agent:")
            print(content.text)

if __name__ == "__main__":
    asyncio.run(main())