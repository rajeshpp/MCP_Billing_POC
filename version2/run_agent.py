import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Load env from repo root .env if present
load_dotenv()

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

async def main(prompt: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    # Where the FastAPI bridge exposes MCP (default to local FastAPI /mcp)
    mcp_url = os.getenv('MCP_TRANSPORT_URL', 'http://127.0.0.1:8000/mcp')

    async with MCPServerStreamableHttp(
        name="BillingStreamable",
        params={
            "url": mcp_url,
        },
        cache_tools_list=True,
    ) as billing_server:
        agent = Agent(
            name="CustomerSupportAgent",
            instructions="You are a support agent. If the user asks about invoices, call the billing MCP tools.",
            mcp_servers=[billing_server],
            model=os.getenv('AGENT_MODEL', 'gpt-4o-mini'),
            model_settings=ModelSettings(tool_choice="auto"),
        )

        result = await Runner.run(agent, prompt)
        # Serialize final_output and structured steps
        out = {
            'final_output': result.final_output,
            'tool_calls': [
                {
                    'name': step.name,
                    'type': step.type,
                    'output': getattr(step, 'output', None)
                } for step in getattr(result, 'steps', [])
            ]
        }
        print(json.dumps(out))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: run_agent.py "your prompt here"', file=sys.stderr)
        sys.exit(2)
    prompt = sys.argv[1]
    try:
        asyncio.run(main(prompt))
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
