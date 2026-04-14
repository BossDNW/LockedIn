from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models.user import *
from app.utilities.flash import flash
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.routers import templates

router = APIRouter(tags=["Programmes"])

@router.get("/programmes", response_class=HTMLResponse)
async def programmes_page(request: Request, db: SessionDep, user: AuthDep):
    """Render the programmes page"""
    return templates.TemplateResponse(
        request=request,
        name="programmes.html",
        context={"user": user}
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
