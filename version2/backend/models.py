from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./billing.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="unpaid")
    pdf_url = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "pdf_url": self.pdf_url,
        }
