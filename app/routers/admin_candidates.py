from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.routers import templates
from typing import Optional
from sqlmodel import select, func
from app.models.user import Application, User, Programme, Company

router = APIRouter(tags=["Admin Candidates"])

# HTML PAGE - Admin view all candidates
@router.get("/admin/candidates", response_class=HTMLResponse)
async def admin_candidates_page(request: Request, user: AdminDep):
    """Render the admin candidates page - ONLY ADMINS CAN ACCESS"""
    return templates.TemplateResponse(
        request=request,
        name="admin_candidates.html",
        context={"user": user}
    )

# API - Get all applications for admin
@router.get("/api/admin/candidates")
async def get_admin_candidates(
    db: SessionDep,
    user: AdminDep,
    status: Optional[str] = Query(default=None),
    programme_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get all applications for admin to review"""
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    offset = (page - 1) * limit
    
    query = (
        select(Application, User, Programme, Company)
        .join(User, Application.userId == User.id)
        .join(Programme, Application.programmeId == Programme.id)
        .join(Company, Programme.companyId == Company.id)
    )
    
    if status:
        query = query.where(Application.status == status)
    
    if programme_id:
        query = query.where(Application.programmeId == programme_id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.exec(count_query).one()
    
    applications = db.exec(query.offset(offset).limit(limit).order_by(Application.id.desc())).all()
    
    # Get all programmes for filter dropdown
    all_programmes = db.exec(select(Programme, Company).join(Company)).all()
    
    results = []
    for app, student, programme, company in applications:
        results.append({
            "application_id": app.id,
            "student_name": student.username,
            "student_email": student.email,
            "programme_title": programme.title,
            "company_name": company.name,
            "status": app.status,
        })
    
    programmes_list = [{"id": p.id, "title": p.title, "company": c.name} for p, c in all_programmes]
    
    return {
        "data": results,
        "programmes": programmes_list,
        "pagination": {
            "current_page": page,
            "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 1,
            "total_count": total_count,
            "has_next": offset + limit < total_count,
            "has_prev": page > 1
        }
    }

# API - Admin shortlists a student
@router.put("/api/admin/candidates/{application_id}/shortlist")
async def admin_shortlist_candidate(
    db: SessionDep,
    user: AdminDep,
    application_id: int
):
    """Admin shortlists a student - moves from pending to shortlisted"""
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot shortlist: current status is {application.status}")
    
    application.status = "shortlisted"
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {"message": "Student shortlisted successfully", "status": application.status}