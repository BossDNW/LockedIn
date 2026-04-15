from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.models.user import User, StudentProfile, CompanyProfile, AdminProfile, Company
from app.dependencies.auth import AuthDep
from . import templates

router = APIRouter(tags=["Profile"])

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: SessionDep, user: AuthDep):
    
    profile_data = None
    company_data = None
    
    if user.role == 'student':
        profile_data = db.exec(select(StudentProfile).where(StudentProfile.userId == user.id)).first()
    elif user.role == 'company':
        profile_data = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
        company_data = db.exec(select(Company).where(Company.id == user.id)).first()
    elif user.role == 'admin':
        profile_data = db.exec(select(AdminProfile).where(AdminProfile.userId == user.id)).first()
    
    combined_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "name": profile_data.name if profile_data and profile_data.name else user.username,
        "phone": profile_data.contact if profile_data else "",
        "description": profile_data.bio if profile_data else "",
        "profile_picture": profile_data.profilePicture if profile_data and profile_data.profilePicture else "",
        "location": profile_data.location if user.role == 'company' and profile_data else "",
        "website": profile_data.website if user.role == 'company' and profile_data else "",
    }
    
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": combined_data}
    )

@router.get("/edit-profile", response_class=HTMLResponse)
async def edit_profile_page(request: Request, db: SessionDep, user: AuthDep):
    
    profile_data = None
    company_data = None
    
    if user.role == 'student':
        profile_data = db.exec(select(StudentProfile).where(StudentProfile.userId == user.id)).first()
    elif user.role == 'company':
        profile_data = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
        company_data = db.exec(select(Company).where(Company.id == user.id)).first()
    elif user.role == 'admin':
        profile_data = db.exec(select(AdminProfile).where(AdminProfile.userId == user.id)).first()
    
    combined_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "name": profile_data.name if profile_data and profile_data.name else user.username,
        "phone": profile_data.contact if profile_data else "",
        "description": profile_data.bio if profile_data else "",
        "profile_picture": profile_data.profilePicture if profile_data and profile_data.profilePicture else "",
        "location": profile_data.location if user.role == 'company' and profile_data else "",
        "website": profile_data.website if user.role == 'company' and profile_data else "",
    }
    
    return templates.TemplateResponse(
        request=request,
        name="edit-profile.html",
        context={"user": combined_data}
    )

@router.post("/update-profile")
async def update_profile(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    email: str = Form(None),
    username: str = Form(None),
    phone: str = Form(None),
    description: str = Form(None),
    location: str = Form(None),
    website: str = Form(None),
    profile_picture: str = Form(None)  
):
    
    db_user = db.exec(select(User).where(User.id == user.id)).one()
    
    if email and email != user.email:
        db_user.email = email
        db.add(db_user)
    
    if user.role == 'student':
        profile = db.exec(select(StudentProfile).where(StudentProfile.userId == user.id)).first()
        if profile:
            if phone is not None:
                profile.contact = phone if phone else ""
            if description is not None:
                profile.bio = description if description else ""
            if username and username != profile.name:
                profile.name = username
            if profile_picture is not None:
                profile.profilePicture = profile_picture if profile_picture else ""
            db.add(profile)
        else:
            profile = StudentProfile(
                userId=user.id,
                name=username or user.username,
                contact=phone or "",
                bio=description or "",
                profilePicture=profile_picture or "",
                resume=""
            )
            db.add(profile)
            
    elif user.role == 'company':
        profile = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
        company = db.exec(select(Company).where(Company.id == user.id)).first()
        
        if profile:
            if location is not None:
                profile.location = location if location else ""
            if website is not None:
                profile.website = website if website else ""
            if phone is not None:
                profile.contact = phone if phone else ""
            if description is not None:
                profile.bio = description if description else ""
            if username and username != profile.name:
                profile.name = username
            if profile_picture is not None:
                profile.profilePicture = profile_picture if profile_picture else ""
            db.add(profile)
        else:
            profile = CompanyProfile(
                userId=user.id,
                name=username or user.username,
                contact=phone or "",
                bio=description or "",
                profilePicture=profile_picture or "",
                location=location or "",
                website=website or ""
            )
            db.add(profile)
      
        if company:
            if username:
                company.name = username
                db.add(company)
        else:
            new_company = Company(id=user.id, name=username or user.username)
            db.add(new_company)
            
    elif user.role == 'admin':
        profile = db.exec(select(AdminProfile).where(AdminProfile.userId == user.id)).first()
        if profile:
            if phone is not None:
                profile.contact = phone if phone else ""
            if description is not None:
                profile.bio = description if description else ""
            if username and username != profile.name:
                profile.name = username
            if profile_picture is not None:
                profile.profilePicture = profile_picture if profile_picture else ""
            db.add(profile)
        else:
            profile = AdminProfile(
                userId=user.id,
                name=username or user.username,
                contact=phone or "",
                bio=description or "",
                profilePicture=profile_picture or ""
            )
            db.add(profile)
    
    db.commit()
    
    return RedirectResponse(url="/profile", status_code=303)