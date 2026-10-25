from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    DateTime,
)

from sqlalchemy.orm import relationship

from .database import Base

from datetime import datetime


# =========================
# COMPANY / BUSINESS
# =========================

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    website = Column(String, nullable=True)

    plan_id = Column(Integer, ForeignKey("plan.id"), nullable=True)
    plan = relationship("Plan")


# =========================
# CUSTOMER
# =========================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    company = relationship("Company")

    orders = relationship(
        "Order",
        back_populates="customer"
    )

    tickets = relationship(
        "Ticket",
        back_populates="customer"
    )

    conversations = relationship(
        "Conversation",
        back_populates="customer"
    )


# =========================
# ORDER
# =========================

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, nullable=False, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    status = Column(String, nullable=False)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    company = relationship("Company")

    customer = relationship(
        "Customer",
        back_populates="orders"
    )


# =========================
# PRODUCT
# =========================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)


# =========================
# TICKET
# =========================

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, unique=True, nullable=False, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    subject = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    company = relationship("Company")

    customer = relationship(
        "Customer",
        back_populates="tickets"
    )


# =========================
# USER
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    hashed_password = Column(String, nullable=False)

    role = Column(
        String,
        nullable=False,
        default="customer"
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=True
    )

    company = relationship("Company")


# =========================
# CONVERSATION
# =========================

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    company = relationship("Company")

    customer = relationship(
        "Customer",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation"
    )


# =========================
# MESSAGE
# =========================

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    sender = Column(String, nullable=False)
    message = Column(String, nullable=False)

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )


# =========================
# COMPANY USAGE
# =========================

class CompanyUsage(Base):
    __tablename__ = "company_usage"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        unique=True
    )

    ai_messages_used = Column(
        Integer,
        nullable=False,
        default=0
    )

    customers_used = Column(
        Integer,
        nullable=False,
        default=0
    )

    documents_used = Column(
        Integer,
        nullable=False,
        default=0
    )

    company = relationship("Company")


# =========================
# PLAN
# =========================

class Plan(Base):
    __tablename__ = "plan"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(50),
        nullable=False
    )

    price_monthly = Column(
        Numeric(10, 2),
        nullable=False
    )

    max_cutomers = Column(
        Integer,
        nullable=False,
        default=100
    )

    max_ai_messages = Column(
        Integer,
        nullable=False,
        default=100
    )

    max_documents = Column(
        Integer,
        nullable=False,
        default=5
    )


# =========================
# SUBSCRIPTION
# =========================

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        unique=True
    )

    plan_id = Column(
        Integer,
        ForeignKey("plan.id"),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="trial"
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    expires_at = Column(
        DateTime,
        nullable=True
    )

    company = relationship("Company")

    plan = relationship("Plan")