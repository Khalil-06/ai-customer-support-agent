from fastapi import FastAPI, Depends
from pydantic import BaseModel

from .database import engine, Base, SessionLocal
from . import models


# -------------------------
# APP SETUP
# -------------------------

app = FastAPI()

Base.metadata.create_all(bind=engine)


# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# -------------------------
# HOME
# -------------------------

@app.get("/")
def home():
    return {
        "message": "AI Customer Support Agent is running!"
    }


# -------------------------
# ORDER API
# -------------------------

orders = {
    1001: "Shipped",
    1002: "Delivered",
    1003: "Processing"
}


@app.get("/orders/{order_id}")
def get_order_status(order_id: int):

    if order_id in orders:
        return {
            "order_id": order_id,
            "status": orders[order_id]
        }

    return {
        "order_id": order_id,
        "status": "Order not found"
    }


# -------------------------
# PRODUCT API
# -------------------------

products = {
    101: {
        "name": "Wireless Headphones",
        "price": 1999,
        "stock": 15
    },
    102: {
        "name": "Smart Watch",
        "price": 2999,
        "stock": 8
    },
    103: {
        "name": "Bluetooth Speaker",
        "price": 1499,
        "stock": 20
    }
}


@app.get("/products/{product_id}")
def get_product(product_id: int):

    if product_id in products:
        return {
            "product_id": product_id,
            "product": products[product_id]
        }

    return {
        "product_id": product_id,
        "message": "Product not found"
    }


# -------------------------
# SUPPORT TICKET API
# -------------------------

class Ticket(BaseModel):
    customer_name: str
    email: str
    issue: str


tickets = []

next_ticket_id = 1


@app.post("/tickets")
def create_ticket(ticket: Ticket):

    global next_ticket_id

    new_ticket = {
        "ticket_id": next_ticket_id,
        "customer_name": ticket.customer_name,
        "email": ticket.email,
        "issue": ticket.issue,
        "status": "Open"
    }

    tickets.append(new_ticket)

    next_ticket_id += 1

    return {
        "message": "Support ticket created successfully",
        "ticket": new_ticket
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):

    for ticket in tickets:

        if ticket["ticket_id"] == ticket_id:
            return ticket

    return {
        "message": "Ticket not found"
    }


# -------------------------
# CUSTOMER SCHEMA
# -------------------------

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str


# -------------------------
# CREATE CUSTOMER
# -------------------------

@app.post("/customers")
def create_customer(
    customer: CustomerCreate,
    db=Depends(get_db)
):

    new_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {
        "message": "Customer created successfully",
        "customer": {
            "id": new_customer.id,
            "name": new_customer.name,
            "email": new_customer.email,
            "phone": new_customer.phone
        }
    }


# -------------------------
# GET CUSTOMER
# -------------------------

@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db=Depends(get_db)
):

    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if customer:

        return {
            "customer_id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        }

    return {
        "customer_id": customer_id,
        "message": "Customer not found"
    }