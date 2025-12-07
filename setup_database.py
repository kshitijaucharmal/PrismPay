import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from faker import Faker

# --- 1. Database Configuration ---
# REPLACE with your actual Postgres URL: postgresql://user:password@localhost/dbname
DATABASE_URL = "postgresql://postgres:password@localhost/onecard_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
fake = Faker('en_IN')  # Indian context for names/addresses

# --- 2. Define Tables (Schema) ---


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)
    status = Column(String, default="verified")  # verified, pending, blocked
    credit_limit = Column(Float, default=100000.0)
    balance_due = Column(Float, default=0.0)
    min_due = Column(Float, default=0.0)
    due_date = Column(Date, nullable=True)

    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
    cards = relationship("Card", back_populates="customer")


class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    card_number = Column(String, unique=True)  # Masked in real life
    status = Column(String, default="active")  # active, blocked, in_transit
    # delivered, out_for_delivery
    delivery_status = Column(String, default="delivered")
    tracking_id = Column(String, nullable=True)

    customer = relationship("Customer", back_populates="cards")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    merchant = Column(String)
    amount = Column(Float)
    category = Column(String)  # Food, Travel, Shopping, Repayment
    date = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="transactions")

# --- 3. Data Seeding Function ---


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if data exists
    if db.query(Customer).count() > 0:
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding database with 100 customers and transactions...")

    for _ in range(100):
        # Create Customer
        cust_id = f"cust_{uuid.uuid4().hex[:8]}"
        is_overdue = random.choice(
            [True, False, False])  # 33% chance of overdue

        balance = round(random.uniform(1000, 50000), 2) if is_overdue else 0
        due_date = datetime.now() + timedelta(days=random.randint(-5, 20))

        customer = Customer(
            id=cust_id,
            name=fake.name(),
            phone=fake.phone_number(),
            status="verified",
            credit_limit=random.choice([50000, 100000, 200000]),
            balance_due=balance,
            min_due=balance * 0.05,
            due_date=due_date.date()
        )
        db.add(customer)

        # Create Card
        card = Card(
            id=f"card_{uuid.uuid4().hex[:8]}",
            customer_id=cust_id,
            card_number=fake.credit_card_number(card_type="visa"),
            status="active",
            delivery_status=random.choice(
                ["delivered", "in_transit", "pending"]),
            tracking_id=f"TRK_{uuid.uuid4().hex[:8].upper()}"
        )
        db.add(card)

        # Create 5-10 Transactions per customer
        for _ in range(random.randint(5, 10)):
            txn = Transaction(
                id=f"txn_{uuid.uuid4().hex[:8]}",
                customer_id=cust_id,
                merchant=fake.company(),
                amount=round(random.uniform(100, 5000), 2),
                category=random.choice(
                    ["Food", "Travel", "Utilities", "Shopping"]),
                date=fake.date_time_between(start_date='-30d', end_date='now')
            )
            db.add(txn)

    db.commit()
    print("Seeding Complete!")
    db.close()


if __name__ == "__main__":
    seed_database()
