from models import Base, engine, SessionLocal, Invoice

Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    db.query(Invoice).delete()
    demo = [
        Invoice(invoice_id="INV-123", customer_id="CUST-1", amount=120.5, currency="USD", status="paid", pdf_url="https://files.local/invoices/INV-123.pdf"),
        Invoice(invoice_id="INV-124", customer_id="CUST-1", amount=200.0, currency="USD", status="unpaid", pdf_url="https://files.local/invoices/INV-124.pdf"),
        Invoice(invoice_id="INV-125", customer_id="CUST-2", amount=75.25, currency="USD", status="paid", pdf_url="https://files.local/invoices/INV-125.pdf"),
        Invoice(invoice_id="INV-126", customer_id="CUST-3", amount=450.00, currency="USD", status="unpaid", pdf_url="https://files.local/invoices/INV-126.pdf"),
    ]
    db.add_all(demo)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
    print("DB seeded")
