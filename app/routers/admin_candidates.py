# app/routers/admin_candidates.py

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.routers import templates
from typing import Optional
from sqlmodel import select, func, or_
from app.models.user import Application, User, Programme, Company, StudentProfile

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
    offset = (page - 1) * limit
    
    # Build the query with all joins
    query = (
        select(Application, User, Programme, Company, StudentProfile)
        .join(User, Application.userId == User.id)
        .join(Programme, Application.programmeId == Programme.id)
        .join(Company, Programme.companyId == Company.id)
        .join(StudentProfile, User.id == StudentProfile.userId, isouter=True)
    )
    
    # Apply filters
    if status and status != 'all':
        query = query.where(Application.status == status)
    
    if programme_id and programme_id != 'all':
        query = query.where(Application.programmeId == programme_id)
    
    # Get total count for pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.exec(count_query).one()
    
    # Execute paginated query
    results = db.exec(
        query.order_by(Application.id.desc()).offset(offset).limit(limit)
    ).all()
    
    # Get all programmes for filter dropdown
    all_programmes = db.exec(
        select(Programme, Company)
        .join(Company, Programme.companyId == Company.id)
        .order_by(Programme.title)
    ).all()
    
    # Format the results
    applications_data = []
    for app, student, programme, company, student_profile in results:
        applications_data.append({
            "application_id": app.id,
            "student_id": student.id,
            "student_name": student.username,
            "student_email": student.email,
            "student_contact": student_profile.contact if student_profile else "Not provided",
            "student_bio": student_profile.bio if student_profile else "Not provided",
            "has_resume": bool(student_profile and student_profile.resume),
            "programme_id": programme.id,
            "programme_title": programme.title,
            "company_name": company.name,
            "status": app.status,
        })
    
    # Format programmes for dropdown
    programmes_list = [
        {
            "id": p.id, 
            "title": p.title, 
            "company": c.name
        } 
        for p, c in all_programmes
    ]
    
    # Calculate pagination
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    return {
        "data": applications_data,
        "programmes": programmes_list,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "limit": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
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
    
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status == "shortlisted":
        raise HTTPException(status_code=400, detail="Student is already shortlisted")
    
    if application.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot shortlist: current status is '{application.status}'"
        )
    
    application.status = "shortlisted"
    db.add(application)
    db.commit()
    db.refresh(application)
    
    student = db.get(User, application.userId)
    programme = db.get(Programme, application.programmeId)
    
    return {
        "message": f"Student {student.username} has been shortlisted for {programme.title}",
        "status": application.status,
        "application_id": application_id
    }


# API - Admin removes shortlist (reverts to pending)
@router.put("/api/admin/candidates/{application_id}/remove-shortlist")
async def admin_remove_shortlist(
    db: SessionDep,
    user: AdminDep,
    application_id: int
):
    """Admin removes shortlist - reverts from shortlisted to pending"""
    
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != "shortlisted":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot remove shortlist: current status is '{application.status}'"
        )
    
    application.status = "pending"
    db.add(application)
    db.commit()
    db.refresh(application)
    
    student = db.get(User, application.userId)
    programme = db.get(Programme, application.programmeId)
    
    return {
        "message": f"Shortlist removed for {student.username} from {programme.title}",
        "status": application.status,
        "application_id": application_id
    }


# API - Get student profile details including resume
@router.get("/api/admin/student/{student_id}")
async def get_student_profile(
    db: SessionDep,
    user: AdminDep,
    student_id: int
):
    """Get detailed student profile including resume"""
    
    # Get student user
    student = db.get(User, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.role != 'student':
        raise HTTPException(status_code=400, detail="User is not a student")
    
    # Get student profile
    student_profile = db.exec(
        select(StudentProfile).where(StudentProfile.userId == student_id)
    ).first()
    
    # Get all applications by this student
    applications = db.exec(
        select(Application, Programme, Company)
        .join(Programme, Application.programmeId == Programme.id)
        .join(Company, Programme.companyId == Company.id)
        .where(Application.userId == student_id)
        .order_by(Application.id.desc())
    ).all()
    
    applications_data = []
    for app, programme, company in applications:
        applications_data.append({
            "application_id": app.id,
            "programme_title": programme.title,
            "company_name": company.name,
            "status": app.status,
            "applied_date": app.id  # You can add created_at field later
        })
    
    return {
        "student": {
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "role": student.role
        },
        "profile": {
            "name": student_profile.name if student_profile else "Not provided",
            "contact": student_profile.contact if student_profile else "Not provided",
            "bio": student_profile.bio if student_profile else "Not provided",
            "profilePicture": student_profile.profilePicture if student_profile else "",
            "resume": student_profile.resume if student_profile else "",
            "has_resume": bool(student_profile and student_profile.resume)
        },
        "applications": applications_data
    }


# API - Download resume
@router.get("/api/admin/student/{student_id}/resume")
async def download_student_resume(
    db: SessionDep,
    user: AdminDep,
    student_id: int
):
    """Download student's resume"""
    
    student = db.get(User, student_id)
    if not student or student.role != 'student':
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_profile = db.exec(
        select(StudentProfile).where(StudentProfile.userId == student_id)
    ).first()
    
    if not student_profile or not student_profile.resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Return the resume content
    return JSONResponse(content={
        "resume": student_profile.resume,
        "student_name": student.username
    })


# API - Get application statistics for admin dashboard
@router.get("/api/admin/candidates/stats")
async def get_admin_candidates_stats(
    db: SessionDep,
    user: AdminDep
):
    """Get statistics about applications for admin dashboard"""
    
    pending_count = db.exec(
        select(func.count()).select_from(Application).where(Application.status == "pending")
    ).one()
    
    shortlisted_count = db.exec(
        select(func.count()).select_from(Application).where(Application.status == "shortlisted")
    ).one()
    
    accepted_count = db.exec(
        select(func.count()).select_from(Application).where(Application.status == "accepted")
    ).one()
    
    rejected_count = db.exec(
        select(func.count()).select_from(Application).where(Application.status == "rejected")
    ).one()
    
    total_count = db.exec(
        select(func.count()).select_from(Application)
    ).one()
    
    return {
        "pending": pending_count,
        "shortlisted": shortlisted_count,
        "accepted": accepted_count,
        "rejected": rejected_count,
        "total": total_count
    }