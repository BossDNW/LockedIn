from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.routers import templates
from typing import Optional
from sqlmodel import select, func
from app.models.user import Programme, Application, User, StudentProfile

router = APIRouter(tags=["Candidates"])


@router.get("/candidates", response_class=HTMLResponse)
async def candidates_page(request: Request, user: AuthDep):
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



@router.get("/api/candidates/student/{student_id}")
async def get_student_profile(
    db: SessionDep,
    user: AuthDep,
    student_id: int
):
    if user.role != 'company':
        raise HTTPException(status_code=403, detail="Access denied")
    
    student = db.get(User, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.role != 'student':
        raise HTTPException(status_code=400, detail="User is not a student")
    

    student_profile = db.exec(
        select(StudentProfile).where(StudentProfile.userId == student_id)
    ).first()
    
    company_programmes = db.exec(
        select(Programme).where(Programme.companyId == user.id)
    ).all()
    programme_ids = [p.id for p in company_programmes]
    
    applications = db.exec(
        select(Application, Programme)
        .join(Programme, Application.programmeId == Programme.id)
        .where(Application.userId == student_id)
        .where(Application.programmeId.in_(programme_ids))
        .order_by(Application.id.desc())
    ).all()
    
    applications_data = []
    for app, programme in applications:
        applications_data.append({
            "application_id": app.id,
            "programme_title": programme.title,
            "status": app.status,
            "applied_date": app.id  
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


@router.get("/api/candidates")
async def get_candidates(
    db: SessionDep,
    user: AuthDep,
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):

    if user.role != 'company':
        raise HTTPException(status_code=403, detail="Access denied")
    
    offset = (page - 1) * limit
    
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
    
    query = (
        select(Application, User, Programme, StudentProfile)
        .join(User, Application.userId == User.id)
        .join(Programme, Application.programmeId == Programme.id)
        .join(StudentProfile, User.id == StudentProfile.userId, isouter=True)
        .where(Application.programmeId.in_(programme_ids))
        .where(Application.status.in_(["shortlisted", "accepted", "rejected", "waitlisted"]))
        .order_by(Application.id.desc())
    )
    
    if status and status != 'all':
        query = query.where(Application.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.exec(count_query).one() or 0
    
    applications = db.exec(query.offset(offset).limit(limit)).all()
    
    results = []
    for app, student, programme, student_profile in applications:
        results.append({
            "application_id": app.id,
            "student_id": student.id,
            "student_name": student.username,
            "student_email": student.email,
            "programme_title": programme.title,
            "status": app.status,
            "has_resume": bool(student_profile and student_profile.resume)
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


@router.get("/api/candidates/stats")
async def get_candidates_stats(
    db: SessionDep,
    user: AuthDep
):
    if user.role != 'company':
        raise HTTPException(status_code=403, detail="Access denied")
    
    programmes = db.exec(
        select(Programme).where(Programme.companyId == user.id)
    ).all()
    
    programme_ids = [p.id for p in programmes]
    
    if not programme_ids:
        return {
            "shortlisted": 0,
            "accepted": 0,
            "rejected": 0,
            "waitlisted": 0,
            "total": 0
        }

    shortlisted = db.exec(
        select(func.count()).select_from(Application).where(
            Application.programmeId.in_(programme_ids),
            Application.status == "shortlisted"
        )
    ).one() or 0
    
    accepted = db.exec(
        select(func.count()).select_from(Application).where(
            Application.programmeId.in_(programme_ids),
            Application.status == "accepted"
        )
    ).one() or 0
    
    rejected = db.exec(
        select(func.count()).select_from(Application).where(
            Application.programmeId.in_(programme_ids),
            Application.status == "rejected"
        )
    ).one() or 0
    
    waitlisted = db.exec(
        select(func.count()).select_from(Application).where(
            Application.programmeId.in_(programme_ids),
            Application.status == "waitlisted"
        )
    ).one() or 0
    
    return {
        "shortlisted": shortlisted,
        "accepted": accepted,
        "rejected": rejected,
        "waitlisted": waitlisted,
        "total": shortlisted + accepted + rejected + waitlisted
    }


@router.put("/api/candidates/{application_id}/status")
async def update_candidate_status(
    db: SessionDep,
    user: AuthDep,
    application_id: int,
    status: str
):
    if user.role != 'company':
        raise HTTPException(status_code=403, detail="Access denied")
    
    if status not in ["accepted", "rejected", "waitlisted", "shortlisted"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be accepted, rejected, waitlisted, or shortlisted")
    
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    programme = db.get(Programme, application.programmeId)
    if programme.companyId != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    old_status = application.status
    application.status = status
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {
        "message": f"Candidate status changed from {old_status} to {status} successfully",
        "status": application.status,
        "application_id": application_id
    }