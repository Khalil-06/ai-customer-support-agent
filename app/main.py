from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, Base
from . import models

from .security import hash_password, verify_password
from .auth import create_access_token, decode_access_token

from .ai import generate_ai_response
from .rag import generate_rag_response
from fastapi import HTTPException

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI Customer Support Agent",
    description="Backend API for an AI-powered customer support system",
    version="1.0.0"
)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# PYDANTIC REQUEST MODELS
# =========================================================

class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    phone: str = Field(min_length=7, max_length=20)


class TicketCreate(BaseModel):
    ticket_id: int = Field(gt=0)
    customer_id: int = Field(gt=0)
    subject: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=5, max_length=2000)
    status: str = Field(
        default="Open",
        min_length=1,
        max_length=50
    )


class OrderCreate(BaseModel):
    order_id: int = Field(gt=0)
    customer_id: int = Field(gt=0)
    status: str = Field(min_length=1, max_length=50)


class OrderUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=50)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(
        default="customer",
        min_length=1,
        max_length=20
    )
    company_id: int | None = Field(
        default=None,
        gt=0
    )


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class ConversationCreate(BaseModel):
    customer_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)


class MessageCreate(BaseModel):
    conversation_id: int = Field(gt=0)
    sender: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=5000)


class ChatRequest(BaseModel):
    conversation_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=1000)


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    website: str | None = None


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    print("\n================ REAL ERROR ================\n")
    print(f"Error: {exc}")

    import traceback
    traceback.print_exc()

    print("\n============================================\n")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
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

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        company_id = payload.get("company_id")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "id": int(user_id),
            "email": email,
            "role": role,
            "company_id": company_id
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# =========================================================
# ROLE CHECK
# =========================================================

def require_role(required_role: str):

    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return role_checker


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    logger.info("Home endpoint accessed")

    return {
        "message": "AI Customer Support Agent is running"
    }


# =========================================================
# COMPANY APIs
# =========================================================

@app.post("/companies")
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    existing_company = db.query(models.Company).filter(
        models.Company.email == company.email
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="Company email already registered"
        )

    new_company = models.Company(
        name=company.name,
        email=company.email,
        website=company.website
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return {
        "message": "Company created successfully",
        "company": {
            "id": new_company.id,
            "name": new_company.name,
            "email": new_company.email,
            "website": new_company.website
        }
    }


@app.post("/companies/register")
def register_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    existing_company = db.query(models.Company).filter(
        models.Company.email == company.email
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="Company email already registered"
        )

    new_company = models.Company(
        name=company.name,
        email=company.email,
        website=company.website
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return {
        "message": "Company registration successful",
        "company": {
            "id": new_company.id,
            "name": new_company.name,
            "email": new_company.email
        }
    }


# =========================================================
# CUSTOMER APIs
# =========================================================

@app.post("/customers")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    if company_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a company"
        )

    existing_customer = db.query(models.Customer).filter(
        models.Customer.email == customer.email,
        models.Customer.company_id == company_id
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer email already exists"
        )

    new_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        company_id=company_id
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
            "phone": new_customer.phone,
            "company_id": new_customer.company_id
        }
    }


@app.get("/customers")
def get_customers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    customers = db.query(models.Customer).filter(
        models.Customer.company_id == company_id
    ).all()

    return customers


@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == current_user["company_id"]
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == current_user["company_id"]
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

    return existing_customer


@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == current_user["company_id"]
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == current_user["company_id"]
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    orders = db.query(models.Order).filter(
        models.Order.customer_id == customer_id,
        models.Order.company_id == current_user["company_id"]
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == current_user["company_id"]
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    tickets = db.query(models.Ticket).filter(
        models.Ticket.customer_id == customer_id,
        models.Ticket.company_id == current_user["company_id"]
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
# ORDER APIs
# =========================================================

@app.post("/orders")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    if company_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a company"
        )

    customer = db.query(models.Customer).filter(
        models.Customer.id == order.customer_id,
        models.Customer.company_id == company_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    existing_order = db.query(models.Order).filter(
        models.Order.order_id == order.order_id,
        models.Order.company_id == company_id
    ).first()

    if existing_order:
        raise HTTPException(
            status_code=400,
            detail="Order ID already exists"
        )

    new_order = models.Order(
        order_id=order.order_id,
        customer_id=order.customer_id,
        status=order.status,
        company_id=company_id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order created successfully",
        "order": {
            "order_id": new_order.order_id,
            "customer_id": new_order.customer_id,
            "status": new_order.status,
            "company_id": new_order.company_id
        }
    }


@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    order = db.query(models.Order).filter(
        models.Order.order_id == order_id,
        models.Order.company_id == company_id
    ).first()

    if not order:
        return {
            "order_id": order_id,
            "message": "Order not found"
        }

    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "status": order.status,
        "company_id": order.company_id
    }


@app.put("/orders/{order_id}")
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    existing_order = db.query(models.Order).filter(
        models.Order.order_id == order_id,
        models.Order.company_id == company_id
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
            "status": existing_order.status,
            "company_id": existing_order.company_id
        }
    }


@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    existing_order = db.query(models.Order).filter(
        models.Order.order_id == order_id,
        models.Order.company_id == company_id
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
# TICKET APIs
# =========================================================

@app.post("/tickets")
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    if company_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a company"
        )

    customer = db.query(models.Customer).filter(
        models.Customer.id == ticket.customer_id,
        models.Customer.company_id == company_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket.ticket_id,
        models.Ticket.company_id == company_id
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
        status=ticket.status,
        company_id=company_id
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
            "status": new_ticket.status,
            "company_id": new_ticket.company_id
        }
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id,
        models.Ticket.company_id == company_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "company_id": ticket.company_id
    }


@app.put("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id,
        models.Ticket.company_id == company_id
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
            "status": existing_ticket.status,
            "company_id": existing_ticket.company_id
        }
    }


@app.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_id == ticket_id,
        models.Ticket.company_id == company_id
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

    if user.company_id is not None:
        company = db.query(models.Company).filter(
            models.Company.id == user.company_id
        ).first()

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

    hashed_password = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        company_id=user.company_id
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
            "role": new_user.role,
            "company_id": new_user.company_id
        }
    }


# =========================================================
# USER LOGIN
# =========================================================

@app.post("/login")
def login_user(
    user: LoginRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for: {user.email}")

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        data={
            "sub": str(existing_user.id),
            "email": existing_user.email,
            "role": existing_user.role,
            "company_id": existing_user.company_id
        }
    )

    logger.info(
        f"Login successful for user ID: {existing_user.id}"
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "name": existing_user.name,
            "email": existing_user.email,
            "role": existing_user.role,
            "company_id": existing_user.company_id
        }
    }


# =========================================================
# ADMIN TEST
# =========================================================

@app.get("/admin-test")
def admin_test(
    current_user: dict = Depends(require_role("admin"))
):
    return {
        "message": "Welcome Admin!",
        "user": current_user
    }


# =========================================================
# CONVERSATIONS
# =========================================================

@app.post("/conversations")
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    if company_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with a company"
        )

    customer = db.query(models.Customer).filter(
        models.Customer.id == conversation.customer_id,
        models.Customer.company_id == company_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    new_conversation = models.Conversation(
        customer_id=conversation.customer_id,
        title=conversation.title,
        company_id=company_id
    )

    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return {
        "message": "Conversation created successfully",
        "conversation": {
            "id": new_conversation.id,
            "customer_id": new_conversation.customer_id,
            "title": new_conversation.title,
            "company_id": new_conversation.company_id
        }
    }


# =========================================================
# MESSAGES
# =========================================================

@app.post("/messages")
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == message.conversation_id,
        models.Conversation.company_id == company_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    new_message = models.Message(
        conversation_id=message.conversation_id,
        sender=message.sender,
        message=message.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {
        "message": "Message created successfully",
        "data": {
            "id": new_message.id,
            "conversation_id": new_message.conversation_id,
            "sender": new_message.sender,
            "message": new_message.message
        }
    }


@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.company_id == company_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(
        models.Message.id
    ).all()

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender,
                "message": msg.message
            }
            for msg in messages
        ]
    }


@app.get("/customers/{customer_id}/conversations")
def get_customer_conversations(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.company_id == company_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    conversations = db.query(models.Conversation).filter(
        models.Conversation.customer_id == customer_id,
        models.Conversation.company_id == company_id
    ).order_by(
        models.Conversation.id
    ).all()

    return {
        "customer_id": customer_id,
        "conversations": [
            {
                "id": conversation.id,
                "title": conversation.title,
                "company_id": conversation.company_id
            }
            for conversation in conversations
        ]
    }

def check_ai_message_limit(db: Session, company_id: int):
    company = db.query(models.Company).filter(
        models.Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    usage = db.query(models.CompanyUsage).filter(
        models.CompanyUsage.company_id == company_id
    ).first()

    if not usage:
        usage = models.CompanyUsage(company_id=company_id)
        db.add(usage)
        db.commit()
        db.refresh(usage)

    plan = db.query(models.Plan).filter(
        models.Plan.id == company.plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=500,
            detail="Company plan not configured"
        )

    if usage.ai_messages_used >= plan.max_ai_messages:
        raise HTTPException(
            status_code=429,
            detail="AI message limit reached for your plan"
        )

    return usage
# =========================================================
# AI CHAT
# =========================================================

@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]

    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == request.conversation_id,
        models.Conversation.company_id == company_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Save customer message
    customer_message = models.Message(
        conversation_id=request.conversation_id,
        sender="customer",
        message=request.message
    )

    db.add(customer_message)
    db.commit()
    db.refresh(customer_message)

    # Generate AI response
    ai_reply = generate_rag_response(request.message, company_id)

    # Save AI response
    ai_message = models.Message(
        conversation_id=request.conversation_id,
        sender="ai",
        message=ai_reply
    )

    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    # Get conversation history
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == request.conversation_id
    ).order_by(
        models.Message.id
    ).all()

    history = [
        {
            "sender": msg.sender,
            "message": msg.message
        }
        for msg in messages
    ]

    return {
        "conversation_id": request.conversation_id,
        "user_message": request.message,
        "reply": ai_reply,
        "history": history
    }