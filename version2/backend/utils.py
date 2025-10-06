from models import SessionLocal, Invoice
from typing import List
import uuid

def get_invoice_by_id(invoice_id: str):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    db.close()
    if not inv:
        return None
    return inv.to_dict()

def list_invoices_for_customer(customer_id: str):
    db = SessionLocal()
    rows = db.query(Invoice).filter(Invoice.customer_id == customer_id).all()
    db.close()
    return [r.to_dict() for r in rows]

def create_invoice(customer_id: str, amount: float, currency: str = "USD", status: str = "unpaid", pdf_url: str | None = None):
    db = SessionLocal()
    inv_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    inv = Invoice(invoice_id=inv_id, customer_id=customer_id, amount=amount, currency=currency, status=status, pdf_url=pdf_url)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    db.close()
    return inv.to_dict()

def update_invoice(invoice_id: str, **fields):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not inv:
        db.close()
        return None
    for k, v in fields.items():
        if hasattr(inv, k):
            setattr(inv, k, v)
    db.commit()
    db.refresh(inv)
    data = inv.to_dict()
    db.close()
    return data

def delete_invoice(invoice_id: str):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not inv:
        db.close()
        return False
    db.delete(inv)
    db.commit()
    db.close()
    return True

def search_invoices(q: str):
    db = SessionLocal()
    rows = db.query(Invoice).filter((Invoice.invoice_id.contains(q)) | (Invoice.customer_id.contains(q))).all()
    db.close()
    return [r.to_dict() for r in rows]

def download_pdf_stub(invoice_id: str):
    data = get_invoice_by_id(invoice_id)
    if not data:
        return None
    return data.get("pdf_url")
