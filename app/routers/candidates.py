from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.routers import templates
from typing import Optional
from sqlmodel import select, func
from app.models.user import Programme, Application, User

router = APIRouter(tags=["Candidates"])

@router.get("/candidates", response_class=HTMLResponse)
async def candidates_page(request: Request, user: AuthDep):
    """Render the candidates page - ONLY COMPANIES CAN ACCESS"""
    if user.role != 'company':
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only companies can view the Candidates page."
        )
    
    return templates.TemplateResponse(
        request=request,
        name="candidates.html",
        context={"user": user}
    )


# API - Get candidates for a company's programmes (shortlisted students only)
@router.get("/api/candidates")
async def get_candidates(
    db: SessionDep,
    user: AuthDep,
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get all candidates who applied to this company's programmes"""
    if user.role != 'company':
        raise HTTPException(status_code=403, detail="Access denied")
    
    offset = (page - 1) * limit
    
    # Get all programmes for this company
    programmes = db.exec(
        select(Programme).where(Programme.companyId == user.id)
    ).all()
    
    programme_ids = [p.id for p in programmes]
    
    if not programme_ids:
        return {
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 1,
                "total_count": 0,
                "has_next": False,
                "has_prev": False
            }
        }
    
    # Get applications for these programmes (only show shortlisted, accepted, rejected, waitlisted)
    query = (
        select(Application, User, Programme)
        .join(User, Application.userId == User.id)
        .join(Programme, Application.programmeId == Programme.id)
        .where(Application.programmeId.in_(programme_ids))
        .where(Application.status.in_(["shortlisted", "accepted", "rejected", "waitlisted"]))
        .order_by(Application.id.desc())
    )
    
    if status and status != 'all':
        query = query.where(Application.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.exec(count_query).one() or 0
    
    applications = db.exec(query.offset(offset).limit(limit)).all()
    
    results = []
    for app, student, programme in applications:
        results.append({
            "application_id": app.id,
            "student_name": student.username,
            "student_email": student.email,
            "programme_title": programme.title,
            "status": app.status,
        })
    
    return {
        "data": results,
        "pagination": {
            "current_page": page,
            "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 1,
            "total_count": total_count,
            "has_next": offset + limit < total_count,
            "has_prev": page > 1
        }
    }


# API - Company updates candidate status (accept/reject/waitlist)
@router.put("/api/candidates/{application_id}/status")
async def update_candidate_status(
    db: SessionDep,
    user: AuthDep,
    application_id: int,
    status: str
):
    """Update candidate status (accept/reject/waitlist) - Only for shortlisted candidates"""
    if user.role != 'company':
        raise HTTPException(status_code=403, detail="Access denied")
    
    if status not in ["accepted", "rejected", "waitlisted"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be accepted, rejected, or waitlisted")
    
    # Verify this application belongs to one of the company's programmes
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    programme = db.get(Programme, application.programmeId)
    if programme.companyId != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Only allow updating if currently shortlisted
    if application.status != "shortlisted":
        raise HTTPException(status_code=400, detail=f"Cannot update: current status is {application.status}. Only shortlisted candidates can be updated.")
    
    application.status = status
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {"message": f"Candidate {status} successfully", "status": application.status}