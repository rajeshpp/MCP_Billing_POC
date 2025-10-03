from mcp.server.fastmcp import FastMCP
from typing import TypedDict

# Initialize MCP server
mcp = FastMCP("BillingServer", website_url="https://billing.local")

# Mock database
INVOICES = {
    "INV-123": {
        "invoice_id": "INV-123",
        "customer_id": "CUST-1",
        "amount": 120.5,
        "currency": "USD",
        "status": "paid",
        "pdf_url": "https://files.local/invoices/INV-123.pdf"
    }
}

class Invoice(TypedDict):
    invoice_id: str
    customer_id: str
    amount: float
    currency: str
    status: str
    pdf_url: str

@mcp.tool()
def get_invoice(invoice_id: str) -> Invoice:
    """Return invoice details by ID"""
    inv = INVOICES.get(invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    return inv

@mcp.tool()
def list_invoices(customer_id: str) -> list[Invoice]:
    """List all invoices for a given customer"""
    return [i for i in INVOICES.values() if i["customer_id"] == customer_id]

if __name__ == "__main__":
    # Run server using streamable HTTP transport
    mcp.run(transport="streamable-http")
