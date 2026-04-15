from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import select, join
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.user import Application, Programme, Company
from app.routers import templates

router = APIRouter(tags=["My Applications"])

@router.get("/my-applications", response_class=HTMLResponse)
async def my_applications_page(request: Request, user: AuthDep):
    if user.role != 'student':
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only students can view their applications."
        )
    
    return templates.TemplateResponse(
        request=request,
        name="my_applications.html",
        context={"user": user}
    )


@router.get("/api/my-applications")
async def get_my_applications(
    db: SessionDep,
    user: AuthDep
):
    
    if user.role != 'student':
        raise HTTPException(status_code=403, detail="Access denied")

    query = (
        select(Application, Programme, Company)
        .join(Programme, Application.programmeId == Programme.id)
        .join(Company, Programme.companyId == Company.id)
        .where(Application.userId == user.id)
        .order_by(Application.id.desc()) 
    )
    
    results = db.exec(query).all()
    
    applications = []
    for app, programme, company in results:
        applications.append({
            "id": app.id,
            "programme_id": programme.id,
            "programme_title": programme.title,
            "company_name": company.name,
            "compensation": programme.compensation,
            "schedule": programme.schedule,
            "work_site": programme.workSite,
            "status": app.status,
            "applied_date": app.id, 
            "description": programme.description
        })
    
    return JSONResponse(content=applications)


@router.get("/api/application-stats")
async def get_application_stats(
    db: SessionDep,
    user: AuthDep
):
    
    if user.role != 'student':
        raise HTTPException(status_code=403, detail="Access denied")

    pending = db.exec(
        select(Application).where(
            Application.userId == user.id,
            Application.status == "pending"
        )
    ).all()
    
    shortlisted = db.exec(
        select(Application).where(
            Application.userId == user.id,
            Application.status == "shortlisted"
        )
    ).all()
    
    accepted = db.exec(
        select(Application).where(
            Application.userId == user.id,
            Application.status == "accepted"
        )
    ).all()
    
    rejected = db.exec(
        select(Application).where(
            Application.userId == user.id,
            Application.status == "rejected"
        )
    ).all()
    
    return JSONResponse(content={
        "pending": len(pending),
        "shortlisted": len(shortlisted),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "total": len(pending) + len(shortlisted) + len(accepted) + len(rejected)
    })


@router.post("/api/withdraw-application/{application_id}")
async def withdraw_application(
    application_id: int,
    db: SessionDep,
    user: AuthDep
):
    
    if user.role != 'student':
        raise HTTPException(status_code=403, detail="Access denied")
    
    application = db.exec(
        select(Application).where(
            Application.id == application_id,
            Application.userId == user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot withdraw application at this stage")

    db.delete(application)
    db.commit()
    
    return JSONResponse(content={"message": "Application withdrawn successfully"})