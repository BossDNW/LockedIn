from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.user import Application
from pydantic import BaseModel
from sqlmodel import select

router = APIRouter(tags=["Applications"])

class ApplicationRequest(BaseModel):
    programmeId: int

# API ROUTE - Apply to a programme (no /api prefix)
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