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
    """Display user profile based on role"""
    
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
        "phone": profile_data.contact if profile_data else "",
        "description": profile_data.bio if profile_data else "",
        "company_name": company_data.name if company_data else "",
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
    """Show edit profile form"""
    
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
        "phone": profile_data.contact if profile_data else "",
        "description": profile_data.bio if profile_data else "",
        "company_name": company_data.name if company_data else "",
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
    # Company-specific fields
    company_name: str = Form(None),
    location: str = Form(None),
    website: str = Form(None)
):
    """Update user profile based on role"""
    
    # Update User table (email and username) - applies to ALL roles
    db_user = db.exec(select(User).where(User.id == user.id)).one()
    
    if email and email != user.email:
        db_user.email = email
        db.add(db_user)
    
    if username and username != user.username:
        db_user.username = username
        db.add(db_user)
    
   
    
    # Update profile based on role
    if user.role == 'student':
        profile = db.exec(select(StudentProfile).where(StudentProfile.userId == user.id)).first()
        if profile:
            if phone is not None:
                profile.contact = phone if phone else ""
            if description is not None:
                profile.bio = description if description else ""
            db.add(profile)
            
    elif user.role == 'company':
        # Update CompanyProfile
        profile = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
        if profile:
            if location is not None:
                profile.location = location if location else ""
            if website is not None:
                profile.website = website if website else ""
            if phone is not None:
                profile.contact = phone if phone else ""
            if description is not None:
                profile.bio = description if description else ""
            db.add(profile)
        
        # Update Company table (company name)
        if company_name is not None:
            company = db.exec(select(Company).where(Company.id == user.id)).first()
            if company:
                company.name = company_name if company_name else ""
                db.add(company)
            else:
                new_company = Company(id=user.id, name=company_name)
                db.add(new_company)
            
    elif user.role == 'admin':
        profile = db.exec(select(AdminProfile).where(AdminProfile.userId == user.id)).first()
        if profile:
            if phone is not None:
                profile.contact = phone if phone else ""
            if description is not None:
                profile.bio = description if description else ""
            db.add(profile)
    
    db.commit()
    
    return RedirectResponse(url="/profile", status_code=303)