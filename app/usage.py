from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


def check_ai_message_limit(db: Session, company_id: int):
    company = db.query(models.Company).filter(
        models.Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    plan = db.query(models.Plan).filter(
        models.Plan.id == company.plan_id
    ).first()

    usage = db.query(models.CompanyUsage).filter(
        models.CompanyUsage.company_id == company_id
    ).first()

    if not plan or not usage:
        raise HTTPException(
            status_code=500,
            detail="Plan or usage data not found"
        )

    if usage.ai_messages_used >= plan.max_ai_messages:
        raise HTTPException(
            status_code=403,
            detail="AI message limit reached. Please upgrade your plan."
        )

    return usage
def check_customer_limit(db: Session, company_id: int):
    company = db.query(models.Company).filter(
        models.Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    plan = db.query(models.Plan).filter(
        models.Plan.id == company.plan_id
    ).first()

    usage = db.query(models.CompanyUsage).filter(
        models.CompanyUsage.company_id == company_id
    ).first()

    if not plan or not usage:
        raise HTTPException(
            status_code=500,
            detail="Plan or usage data not found"
        )

    if usage.customers_used >= plan.max_cutomers:
        raise HTTPException(
            status_code=403,
            detail="Customer limit reached. Please upgrade your plan."
        )

    return usage