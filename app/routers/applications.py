from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.user import Application, Programme, Company
from pydantic import BaseModel
from sqlmodel import select
from datetime import datetime

router = APIRouter(tags=["Applications"])

class ApplicationRequest(BaseModel):
    programmeId: int

# API ROUTE - Apply to a programme
@router.post("/applications")
async def apply_to_programme(
    db: SessionDep,
    user: AuthDep,
    application_data: ApplicationRequest
):
    """Apply to a programme"""
    # Check if already applied
    existing = db.exec(
        select(Application).where(
            Application.userId == user.id,
            Application.programmeId == application_data.programmeId
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this programme")
    
    # Create application
    application = Application(
        userId=user.id,
        programmeId=application_data.programmeId,
        status="pending"
    )
    
    try:
        db.add(application)
        db.commit()
        db.refresh(application)
        return {"message": "Successfully applied", "application_id": application.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# API ROUTE - Get my applications (for students)
@router.get("/my-applications")
async def get_my_applications(db: SessionDep, user: AuthDep):
    """Get all applications for the current user (student view)"""
    applications = db.exec(
        select(Application, Programme, Company)
        .join(Programme, Application.programmeId == Programme.id)
        .join(Company, Programme.companyId == Company.id)
        .where(Application.userId == user.id)
        .order_by(Application.id.desc())
    ).all()
    
    result = []
    for app, programme, company in applications:
        result.append({
            "id": app.id,
            "programme_title": programme.title,
            "company_name": company.name,
            "status": app.status,
            "applied_date": app.id  # You can add a created_at field to Application model
        })
    
    return result