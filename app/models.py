from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, nullable=False, index=True)
    customer_id = Column(
    Integer,
    ForeignKey("customers.id"),
    nullable=False
)

    customer = relationship("Customer", back_populates="orders")
    status = Column(String, nullable=False)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
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

    customer = relationship("Customer", back_populates="tickets")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="customer")