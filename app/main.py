from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "AI Customer Support Agent is running!"
    }


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
customers = {
    1: {
        "name": "Khalil",
        "email": "khalil@example.com",
        "phone": "9876543210"
    },
    2: {
        "name": "Rahul",
        "email": "rahul@example.com",
        "phone": "9876543211"
    },
    3: {
        "name": "Ayesha",
        "email": "ayesha@example.com",
        "phone": "9876543212"
    }
}


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    if customer_id in customers:
        return {
            "customer_id": customer_id,
            "customer": customers[customer_id]
        }

    return {
        "customer_id": customer_id,
        "message": "Customer not found"
    }