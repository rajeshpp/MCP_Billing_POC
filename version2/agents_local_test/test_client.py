import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def run():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            res = await session.call_tool("list_invoices", arguments={"customer_id": "CUST-1"})
            print("list_invoices ->", res.structuredContent)

if __name__ == "__main__":
    asyncio.run(run())
