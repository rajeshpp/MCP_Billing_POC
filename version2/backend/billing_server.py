from mcp.server.fastmcp import FastMCP
from typing import TypedDict
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MCP client libs
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

# Load env
load_dotenv()

from models import Base, engine
from utils import get_invoice_by_id, list_invoices_for_customer, create_invoice, update_invoice, delete_invoice, search_invoices, download_pdf_stub

# ensure DB created
Base.metadata.create_all(bind=engine)

mcp = FastMCP("BillingServer")

class Invoice(TypedDict):
    invoice_id: str
    customer_id: str
    amount: float
    currency: str
    status: str
    pdf_url: str | None

@mcp.tool()
def get_invoice(invoice_id: str) -> Invoice:
    inv = get_invoice_by_id(invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    return inv

@mcp.tool()
def list_invoices(customer_id: str) -> list[Invoice]:
    return list_invoices_for_customer(customer_id)

@mcp.tool()
def create_invoice_tool(customer_id: str, amount: float, currency: str = "USD", status: str = "unpaid", pdf_url: str | None = None) -> Invoice:
    return create_invoice(customer_id, amount, currency, status, pdf_url)

@mcp.tool()
def update_invoice_tool(invoice_id: str, fields: dict) -> Invoice:
    updated = update_invoice(invoice_id, **fields)
    if not updated:
        raise ValueError("Invoice not found")
    return updated

@mcp.tool()
def delete_invoice_tool(invoice_id: str) -> dict:
    ok = delete_invoice(invoice_id)
    return {"deleted": ok}

@mcp.tool()
def search_invoices_tool(q: str) -> list[Invoice]:
    return search_invoices(q)

@mcp.tool()
def download_invoice_pdf(invoice_id: str) -> dict:
    url = download_pdf_stub(invoice_id)
    if not url:
        raise ValueError("Invoice or PDF not found")
    return {"pdf_url": url}

# FastAPI bridge for frontend/testing
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add a root and health endpoint for easier debugging
@app.get("/")
def root():
    return {"status": "ok", "message": "MCP Billing API running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

class CallReq(BaseModel):
    tool: str
    arguments: dict


class AgentReq(BaseModel):
    prompt: str

@app.post('/mcp_call')
async def mcp_call(req: CallReq, request: Request):
    """Bridge endpoint for frontend/tests.
    If MCP_TRANSPORT_URL is set in the environment, forward the call to that URL
    using the streamable HTTP client. Otherwise, call the local tool functions
    directly (in-process fallback).
    """
    logger.info(f"Received /mcp_call request from {request.client}: tool={req.tool} args={req.arguments}")

    MCP_TRANSPORT_URL = os.getenv('MCP_TRANSPORT_URL', '').strip() or 'http://127.0.0.1:9000/mcp'

    # If an external transport is configured, try forwarding
    if MCP_TRANSPORT_URL:
        try:
            logger.info(f"Forwarding to MCP transport at {MCP_TRANSPORT_URL}")
            async with streamablehttp_client(MCP_TRANSPORT_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    res = await session.call_tool(req.tool, arguments=req.arguments)
                    logger.info(f"External MCP call result: {res}")
                    return res.structuredContent
        except Exception:
            logger.exception("External MCP transport failed; falling back to in-process execution")

    # Fallback: call local tool functions directly
    import inspect
    tools = {
        'get_invoice': get_invoice,
        'list_invoices': list_invoices,
        'create_invoice_tool': create_invoice_tool,
        'update_invoice_tool': update_invoice_tool,
        'delete_invoice_tool': delete_invoice_tool,
        'search_invoices_tool': search_invoices_tool,
        'download_invoice_pdf': download_invoice_pdf,
    }

    if req.tool not in tools:
        logger.error(f"Unknown tool requested: {req.tool}")
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown tool: {req.tool}")

    func = tools[req.tool]
    args = req.arguments or {}
    try:
        if inspect.iscoroutinefunction(func):
            result = await func(**args)
        else:
            from starlette.concurrency import run_in_threadpool
            result = await run_in_threadpool(lambda: func(**args))
        return result
    except Exception:
        logger.exception("Error while executing tool in-process")
        raise


@app.get('/routes')
def list_routes():
    """Diagnostic endpoint: list registered routes and methods."""
    routes = []
    for route in app.router.routes:
        try:
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            routes.append({'path': getattr(route, 'path', str(route)), 'methods': methods})
        except Exception:
            continue
    return {'routes': routes}


@app.post('/run_agent')
async def run_agent(req: AgentReq):
    """Run the agent with the provided prompt in a subprocess and return its output.
    This keeps the FastAPI process isolated from the agent runtime and avoids import/path issues.
    Expects a `run_agent.py` script at the repository root that accepts the prompt as argv[1]
    and prints a JSON object (or plain text) to stdout.
    """
    import subprocess
    import sys
    import json

    # repo root (one level up from backend/)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    runner_py = os.path.join(repo_root, 'run_agent.py')
    if not os.path.exists(runner_py):
        raise HTTPException(status_code=500, detail=f"Agent runner not found at {runner_py}")

    cmd = [sys.executable, runner_py, req.prompt]
    logger.info(f"Spawning agent subprocess: {cmd}")
    try:
        proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Agent run timed out")

    if proc.returncode != 0:
        logger.error("Agent subprocess failed: %s", proc.stderr)
        raise HTTPException(status_code=500, detail=f"Agent failed: {proc.stderr}")

    out = proc.stdout.strip()
    # Try to parse JSON output, otherwise return plain text
    try:
        return json.loads(out)
    except Exception:
        return {"output": out}

if __name__ == "__main__":
    # NOTE: For a robust MCP transport run, start the MCP transport in a
    # separate process using `start_mcp.py` (recommended). This module will
    # only start the FastAPI bridge.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
