from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models.user import *
from app.utilities.flash import flash
from sqlmodel import select, or_
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.routers import templates
import json

router = APIRouter(tags=["Programmes"])

@router.get("/programmes", response_class=HTMLResponse)
async def programmes_page(
    request: Request, 
    db: SessionDep, 
    user: AuthDep,
    id: int = None,
    search: str = None,
    year: str = None,  
    field: str = None,
    credits: str = None  
):
    
    year_filter = None
    if year and year.strip():
        try:
            year_filter = int(year)
        except ValueError:
            pass
    
    credits_filter = None
    if credits and credits.strip():
        try:
            credits_filter = int(credits)
        except ValueError:
            pass
    
    query = select(Programme, Company).join(Company, Programme.companyId == Company.id)
    
    if search:
        query = query.where(
            or_(
                Programme.title.contains(search),
                Company.name.contains(search)
            )
        )
    
    if year_filter:
        query = query.where(Programme.academicYear == year_filter)
    
    if field and field.strip():
        query = query.where(Programme.field == field)
    

    if credits_filter:
        query = query.where(Programme.credits == credits_filter)
    
    results = db.exec(query).all()
    
    programmes_list = []
    for programme, company in results:
        keywords_list = []
        if programme.keywords and programme.keywords != "[]":
            try:
                keywords_list = json.loads(programme.keywords)
            except:
                keywords_list = [programme.keywords] if programme.keywords else []
        
        programmes_list.append({
            "id": programme.id,
            "programme_title": programme.title,
            "company_name": company.name,
            "company_location": "N/A",
            "company_id": company.id,
            "academic_year": programme.academicYear,
            "field": programme.field,
            "credits": programme.credits,
            "compensation": programme.compensation,
            "schedule": programme.schedule,
            "workSite": programme.workSite,
            "description": programme.description,
            "overview": programme.description,
            "responsibilities": programme.responsibilities,
            "requirements": programme.requirements,
            "keywords": programme.keywords,
            "keywords_list": keywords_list,
            "numberOfPositions": programme.numberOfPositions,
            "hours": programme.hours,
            "days": programme.days
        })
    
    selected_programme = None
    if id:
        for p in programmes_list:
            if p["id"] == id:
                selected_programme = p
                break
    
    if not selected_programme and programmes_list:
        selected_programme = programmes_list[0]
    
    has_applied = False
    if selected_programme and user.role == 'student':
        application = db.exec(
            select(Application).where(
                Application.userId == user.id,
                Application.programmeId == selected_programme["id"]
            )
        ).first()
        has_applied = application is not None
    
    years = db.exec(select(Programme.academicYear).distinct()).all()
    fields = db.exec(select(Programme.field).distinct().where(Programme.field != "")).all()
    credits_list = db.exec(select(Programme.credits).distinct()).all()
    
    return templates.TemplateResponse(
        request=request,
        name="programmes.html",
        context={
            "user": user,
            "programmes": programmes_list,
            "selected_programme": selected_programme,
            "has_applied": has_applied,
            "search_term": search or "",
            "selected_year": year_filter, 
            "selected_field": field or "",
            "selected_credits": credits_filter,
            "years": sorted(set(years)),
            "fields": sorted(set(fields)),
            "credits_list": sorted(set(credits_list))
        }
    )



@router.get("/post-programme", response_class=HTMLResponse)
async def post_programme(request: Request, db: SessionDep, user: AuthDep):
    if user.role != 'company':
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="post-programme.html",
        context={"user": user}
    )

@router.post("/post-programme", response_class=HTMLResponse)
async def post_programme(
    request: Request,
    db: SessionDep, 
    user: AuthDep,
    title: str = Form(None),
    number_of_positions: str = Form(None),
    year_of_study: str = Form(None),
    field: str = Form(None),
    credits: str = Form(None),
    schedule: str = Form(None),
    hours: str = Form(None),
    days: str = Form(None),
    work_site: str = Form(None),
    compensation: str = Form(None),
    overview: str = Form(None),
    keywords: str = Form(None),
    responsibilities: str = Form(None),
    requirements: str = Form(None)
    ):

    company = db.exec(select(Company).where(Company.id == user.id)).first()

    if company:
        existing_programme = db.exec(
            select(Programme).where(
                Programme.title == title,
                Programme.companyId == company.id
            )
        ).first()
    
    if existing_programme:
        flash(request, f"A programme with the title '{title}' already exists for your company. Please use a different title.", "danger")
        return RedirectResponse(url=request.url_for("post_programme"), status_code=303)

    new_programme_base = ProgrammeBase(
        title=title,
        companyId=company.id,
        academicYear=int(year_of_study),
        credits=int(credits),
        schedule=schedule,
        workSite=work_site,
        compensation=compensation,
        description=overview,
        keywords=keywords,
        responsibilities=responsibilities,
        requirements=requirements,
        numberOfPositions=int(number_of_positions),
        hours=hours,
        days=days,
        field=field
    )
    new_program = Programme.model_validate(new_programme_base)
    new_program.company = company
    db.add(new_program)
    db.commit()
    flash(request, f"Programme '{title}' posted successfully!", "success")
    return RedirectResponse(url="/post-programme", status_code=303)

@router.get("/edit-programme/{programme_id}", response_class=HTMLResponse)
async def edit_programme_page(
    request: Request,
    programme_id: int,
    db: SessionDep,
    user: AuthDep
):
    
    if user.role != 'company':
        flash(request, "Only companies can edit programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    programme = db.get(Programme, programme_id)
    if not programme:
        flash(request, "Programme not found", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    if programme.companyId != user.id:
        flash(request, "You can only edit your own programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    return templates.TemplateResponse(
        request=request,
        name="edit_programme.html",
        context={
            "user": user,
            "programme": programme
        }
    )


@router.post("/edit-programme/{programme_id}", response_class=HTMLResponse)
async def update_programme(
    request: Request,
    programme_id: int,
    db: SessionDep,
    user: AuthDep,
    title: str = Form(None),
    number_of_positions: str = Form(None),
    year_of_study: str = Form(None),
    field: str = Form(None),
    credits: str = Form(None),
    schedule: str = Form(None),
    hours: str = Form(None),
    days: str = Form(None),
    work_site: str = Form(None),
    compensation: str = Form(None),
    overview: str = Form(None),
    keywords: str = Form(None),
    responsibilities: str = Form(None),
    requirements: str = Form(None)
):
    
    if user.role != 'company':
        flash(request, "Only companies can edit programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    programme = db.get(Programme, programme_id)
    if not programme:
        flash(request, "Programme not found", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    

    if programme.companyId != user.id:
        flash(request, "You can only edit your own programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    existing_programme = db.exec(
        select(Programme).where(
            Programme.title == title,
            Programme.companyId == user.id,
            Programme.id != programme_id
        )
    ).first()
    
    if existing_programme:
        flash(request, f"A programme with the title '{title}' already exists for your company. Please use a different title.", "danger")
        return RedirectResponse(url=request.url_for("edit_programme_page", programme_id=programme_id), status_code=303)
   
    programme.title = title
    programme.numberOfPositions = int(number_of_positions) if number_of_positions else 1
    programme.academicYear = int(year_of_study) if year_of_study else 2024
    programme.field = field or ""
    programme.credits = int(credits) if credits else 0
    programme.schedule = schedule or ""
    programme.hours = hours or ""
    programme.days = days or ""
    programme.workSite = work_site or ""
    programme.compensation = compensation or ""
    programme.description = overview or ""
    programme.keywords = keywords if keywords else "[]"
    programme.responsibilities = responsibilities or ""
    programme.requirements = requirements or ""
    
    db.add(programme)
    db.commit()
    
    flash(request, f"Programme '{title}' updated successfully!", "success")
    return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)


@router.get("/delete-programme/{programme_id}")
async def delete_programme(
    request: Request,
    programme_id: int,
    db: SessionDep,
    user: AuthDep
):
    
    if user.role != 'company':
        flash(request, "Only companies can delete programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)

    programme = db.get(Programme, programme_id)
    if not programme:
        flash(request, "Programme not found", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    if programme.companyId != user.id:
        flash(request, "You can only delete your own programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    db.delete(programme)
    db.commit()
    
    flash(request, f"Programme '{programme.title}' deleted successfully!", "success")
    return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)

@router.post("/apply/{programme_id}")
async def apply_to_programme(
    request: Request,
    programme_id: int,
    db: SessionDep,
    user: AuthDep
):
    
    if user.role != 'student':
        flash(request, "Only students can apply to programmes", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    programme = db.get(Programme, programme_id)
    if not programme:
        flash(request, "Programme not found", "danger")
        return RedirectResponse(url=request.url_for("programmes_page"), status_code=303)
    
    existing_application = db.exec(
        select(Application).where(
            Application.userId == user.id,
            Application.programmeId == programme_id
        )
    ).first()
    
    if existing_application:
        flash(request, f"You have already applied to '{programme.title}'", "warning")
        redirect_url = f"/programmes?id={programme_id}"
        return RedirectResponse(url=redirect_url, status_code=303)
    
    new_application = Application(
        userId=user.id,
        programmeId=programme_id,
        status="pending"
    )
    
    db.add(new_application)
    db.commit()
    
    flash(request, f"Successfully applied to '{programme.title}'!", "success")
    
    redirect_url = f"/programmes?id={programme_id}"
    return RedirectResponse(url=redirect_url, status_code=303)