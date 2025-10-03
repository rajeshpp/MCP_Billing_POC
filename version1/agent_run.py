import asyncio
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in .env")


    # Attach the Billing MCP server
    async with MCPServerStreamableHttp(
        name="BillingStreamable",
        params={
            "url": "http://127.0.0.1:8000/mcp",
        },
        cache_tools_list=True,
    ) as billing_server:
        agent = Agent(
            name="CustomerSupportAgent",
            instructions="You are a support agent. If the user asks about invoices, call the billing MCP tools.",
            mcp_servers=[billing_server],
            model="gpt-4o-mini",  # OpenAI model
            model_settings=ModelSettings(tool_choice="auto"),
        )

        result = await Runner.run(agent, "Fetch invoice INV-123 and tell me the payment status.")
        print("Agent output:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
