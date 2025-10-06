"""
Small helper to start the MCP transport that exposes the registered tools over streamable-http.
Run this in a separate terminal when you want the actual MCP transport running.
"""
from billing_server import mcp

if __name__ == "__main__":
    # Configure host/port on the existing FastMCP settings, then run.
    # FastMCP.run() accepts only the transport name; host/port are taken from mcp.settings.
    mcp.settings.host = '127.0.0.1'
    mcp.settings.port = 9000
    mcp.run(transport='streamable-http')
