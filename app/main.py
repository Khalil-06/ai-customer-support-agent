from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, Base
from . import models

from .security import hash_password, verify_password
from .auth import create_access_token, decode_access_token


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI Customer Support Agent",
    description="Backend API for an AI-powered customer support system",
    version="1.0.0"
)


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# JWT AUTHENTICATION
# =========================================================
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "id": int(user_id),
            "email": email,
            "role": role
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI Customer Support Agent is running"
    }


# =========================================================
# CUSTOMER SCHEMAS
# =========================================================

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str


class CustomerUpdate(BaseModel):
    name: str
    email: str
    phone: str


# =========================================================
# CUSTOMER APIs
# =========================================================

@app.post("/customers")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.email == customer.email
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

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


@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone
    }


@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not existing_customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    existing_customer.name = customer.name
    existing_customer.email = customer.email
    existing_customer.phone = customer.phone

    db.commit()
    db.refresh(existing_customer)

    return {
        "message": "Customer updated successfully",
        "customer": {
            "id": existing_customer.id,
            "name": existing_customer.name,
            "email": existing_customer.email,
            "phone": existing_customer.phone
        }
    }


@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not existing_customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(existing_customer)
    db.commit()

    return {
        "message": "Customer deleted successfully"
    }


# =========================================================
# CUSTOMER ORDERS
# =========================================================

@app.get("/customers/{customer_id}/orders")
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    orders = db.query(models.Order).filter(
        models.Order.customer_id == customer_id
    ).all()

    return {
        "customer_id": customer_id,
        "orders": [
            {
                "order_id": order.order_id,
                "status": order.status
            }
            for order in orders
        ]
    }


# =========================================================
# CUSTOMER TICKETS
# =========================================================

@app.get("/customers/{customer_id}/tickets")
def get_customer_tickets(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    tickets = db.query(models.Ticket).filter(
        models.Ticket.customer_id == customer_id
    ).all()

    return {
        "customer_id": customer_id,
        "tickets": [
            {
                "ticket_id": ticket.ticket_id,
                "subject": ticket.subject,
                "description": ticket.description,
                "status": ticket.status
            }
            for ticket in tickets
        ]
    }


# =========================================================
# ORDER SCHEMAS
# =========================================================

class OrderCreate(BaseModel):
    order_id: int
    customer_id: int
    status: str


class OrderUpdate(BaseModel):
    status: str


# =========================================================
# ORDER APIs
# =========================================================

@app.post("/orders")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == order.customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    existing_order = db.query(models.Order).filter(
        models.Order.order_id == order.order_id
    ).first()

    if existing_order:
        raise HTTPException(
            status_code=400,
            detail="Order ID already exists"
        )

    new_order = models.Order(
        order_id=order.order_id,
        customer_id=order.customer_id,
        status=order.status
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order created successfully",
        "order": {
            "order_id": new_order.order_id,
            "customer_id": new_order.customer_id,
            "status": new_order.status
        }
    }


@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()

    if not order:
        return {
            "order_id": order_id,
            "message": "Order not found"
        }

    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "status": order.status
    }


@app.put("/orders/{order_id}")
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    existing_order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()

    if not existing_order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    existing_order.status = order.status

    db.commit()
    db.refresh(existing_order)

    return {
        "message": "Order updated successfully",
        "order": {
            "order_id": existing_order.order_id,
            "customer_id": existing_order.customer_id,
            "status": existing_order.status
        }
    }


@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    existing_order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()

    if not existing_order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    db.delete(existing_order)
    db.commit()

    return {
        "message": "Order deleted successfully"
    }


# =========================================================
# PRODUCT SCHEMAS
# =========================================================

class ProductCreate(BaseModel):
    product_id: int
    name: str
    price: int


class ProductUpdate(BaseModel):
    name: str
    price: int


# =========================================================
# PRODUCT APIs
# =========================================================

@app.post("/products")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(models.Product).filter(
        models.Product.product_id == product.product_id
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="Product ID already exists"
        )

    new_product = models.Product(
        product_id=product.product_id,
        name=product.name,
        price=product.price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product": {
            "product_id": new_product.product_id,
            "name": new_product.name,
            "price": new_product.price
        }
    }


@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()

    if not product:
        return {
            "product_id": product_id,
            "message": "Product not found"
        }

    return {
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price
    }


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.name = product.name
    existing_product.price = product.price

    db.commit()
    db.refresh(existing_product)

    return {
        "message": "Product updated successfully",
        "product": {
            "product_id": existing_product.product_id,
            "name": existing_product.name,
            "price": existing_product.price
        }
    }


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    existing_product = db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(existing_product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }


# =========================================================
# TICKET SCHEMAS
# =========================================================

class TicketCreate(BaseModel):
    ticket_id: int
    customer_id: int
    subject: str
    description: str
    status: str


class TicketUpdate(BaseModel):
    subject: str
    description: str
    status: str


# =========================================================
# TICKET APIs
# =========================================================

@app.post("/tickets")
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == ticket.customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket.ticket_id
    ).first()

    if existing_ticket:
        raise HTTPException(
            status_code=400,
            detail="Ticket ID already exists"
        )

    new_ticket = models.Ticket(
        ticket_id=ticket.ticket_id,
        customer_id=ticket.customer_id,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return {
        "message": "Ticket created successfully",
        "ticket": {
            "ticket_id": new_ticket.ticket_id,
            "customer_id": new_ticket.customer_id,
            "subject": new_ticket.subject,
            "description": new_ticket.description,
            "status": new_ticket.status
        }
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return {
            "ticket_id": ticket_id,
            "message": "Ticket not found"
        }

    return {
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status
    }


@app.put("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    db: Session = Depends(get_db)
):
    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id
    ).first()

    if not existing_ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    existing_ticket.subject = ticket.subject
    existing_ticket.description = ticket.description
    existing_ticket.status = ticket.status

    db.commit()
    db.refresh(existing_ticket)

    return {
        "message": "Ticket updated successfully",
        "ticket": {
            "ticket_id": existing_ticket.ticket_id,
            "customer_id": existing_ticket.customer_id,
            "subject": existing_ticket.subject,
            "description": existing_ticket.description,
            "status": existing_ticket.status
        }
    }


@app.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id
    ).first()

    if not existing_ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    db.delete(existing_ticket)
    db.commit()

    return {
        "message": "Ticket deleted successfully"
    }


# =========================================================
# USER REGISTRATION
# =========================================================

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "customer"


@app.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }


# =========================================================
# USER LOGIN
# =========================================================

class UserLogin(BaseModel):
    email: str
    password: str


@app.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = verify_password(
        user.password,
        existing_user.hashed_password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "sub": str(existing_user.id),
        "email": existing_user.email,
        "role": existing_user.role
    })

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "name": existing_user.name,
            "email": existing_user.email,
            "role": existing_user.role
        }
    }


# =========================================================
# PROTECTED USER PROFILE
# =========================================================

@app.get("/me")
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "user": current_user
    }