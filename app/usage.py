from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


# ==========================================
# SUBSCRIPTION VALIDATION
# ==========================================

def check_subscription_status(db: Session, company_id: int):
    """
    Check whether a company's subscription is active
    and has not expired.
    """

    subscription = db.query(models.Subscription).filter(
        models.Subscription.company_id == company_id
    ).first()

    # Preserve existing behavior for companies without a subscription.
    if not subscription:
        return

    # Check subscription status
    if subscription.status in ["expired", "cancelled", "suspended"]:
        raise HTTPException(
            status_code=403,
            detail="Subscription expired or inactive. Please renew your plan."
        )

    # Check subscription expiry date
    if (
        subscription.expires_at
        and subscription.expires_at <= datetime.utcnow()
    ):
        subscription.status = "expired"
        db.commit()

        raise HTTPException(
            status_code=403,
            detail="Your subscription has expired. Please renew your plan."
        )


# ==========================================
# COMPANY VALIDATION
# ==========================================

def get_company_plan_and_usage(db: Session, company_id: int):
    """
    Retrieve company, plan and usage information.
    """

    company = db.query(models.Company).filter(
        models.Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # Validate subscription
    check_subscription_status(db, company_id)

    # Get company plan
    plan = db.query(models.Plan).filter(
        models.Plan.id == company.plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=500,
            detail="Company plan not configured"
        )

    # Get usage record
    usage = db.query(models.CompanyUsage).filter(
        models.CompanyUsage.company_id == company_id
    ).first()

    if not usage:
        usage = models.CompanyUsage(
        company_id=company_id,
        ai_messages_used=0,
        customers_used=0,
        documents_used=0
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return company, plan, usage


# ==========================================
# AI MESSAGE LIMIT
# ==========================================

def check_ai_message_limit(db: Session, company_id: int):
    """
    Check subscription status and AI message limits.
    """

    company, plan, usage = get_company_plan_and_usage(
        db, company_id
    )

    if usage.ai_messages_used >= plan.max_ai_messages:
        raise HTTPException(
            status_code=403,
            detail="AI message limit reached. Please upgrade your plan."
        )

    return usage


# ==========================================
# CUSTOMER LIMIT
# ==========================================

def check_customer_limit(db: Session, company_id: int):
    """
    Check subscription status and customer limits.
    """

    company, plan, usage = get_company_plan_and_usage(
        db, company_id
    )

    customer_count = db.query(models.Customer).filter(
        models.Customer.company_id == company_id
    ).count()

    if customer_count >= plan.max_cutomers:
        raise HTTPException(
            status_code=403,
            detail="Customer limit reached. Please upgrade your plan."
        )

    return usage