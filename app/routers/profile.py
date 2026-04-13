from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.models.user import User, StudentProfile, CompanyProfile, AdminProfile
from app.dependencies.auth import AuthDep
from . import templates

router = APIRouter(tags=["Profile"])

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: SessionDep, user: AuthDep):
    """Display user profile based on role"""
    
    profile_data = None
    
    if user.role == 'student':
        # Get student profile
        profile_data = db.exec(select(StudentProfile).where(StudentProfile.userId == user.id)).first()
    elif user.role == 'company':
        # Get company profile
        profile_data = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
    elif user.role == 'admin':
        # Get admin profile
        profile_data = db.exec(select(AdminProfile).where(AdminProfile.userId == user.id)).first()
    
    # Combine user data with profile data
    combined_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "phone": profile_data.contact if profile_data else None,
        "description": profile_data.bio if profile_data else None,
        "company_name": profile_data.name if user.role == 'company' and profile_data else None,
        "location": profile_data.location if user.role == 'company' and profile_data else None,
        "website": profile_data.website if user.role == 'company' and profile_data else None,
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
    
    if user.role == 'student':
        profile_data = db.exec(select(StudentProfile).where(StudentProfile.userId == user.id)).first()
    elif user.role == 'company':
        profile_data = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
    elif user.role == 'admin':
        profile_data = db.exec(select(AdminProfile).where(AdminProfile.userId == user.id)).first()
    
    combined_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "phone": profile_data.contact if profile_data else "",
        "description": profile_data.bio if profile_data else "",
        "company_name": profile_data.name if user.role == 'company' and profile_data else "",
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
    username: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    description: str = Form(None),
    # Company-specific fields
    company_name: str = Form(None),
    location: str = Form(None),
    website: str = Form(None)
):
    """Update user profile based on role"""
    
    # Update email in User table if changed
    if email and email != user.email:
        db_user = db.exec(select(User).where(User.id == user.id)).one()
        db_user.email = email
        db.add(db_user)


    # Update username in User table if changed
    if username and username != user.username:
        db_user = db.exec(select(User).where(User.id == user.id)).one()
        db_user.username = username
        db.add(db_user)
    
    #Update description in User table if changed
    if description and description != user.description:
        db_user = db.exec(select(User).where(User.id == user.id)).one()
        db_user.description = description
        db.add(db_user)
    
    #Update company name in User table if changed and user is company
    if user.role == 'company' and company_name and company_name != user.name:
        db_user = db.exec(select(User).where(User.id == user.id)).one()
        db_user.name = company_name
        db.add(db_user)
    
    #Update phone in User table if changed    
    if phone and phone != user.phone:
        db_user = db.exec(select(User).where(User.id == user.id)).one()
        db_user.phone = phone
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
        profile = db.exec(select(CompanyProfile).where(CompanyProfile.userId == user.id)).first()
        if profile:
            if company_name is not None:
                profile.name = company_name if company_name else ""
            if location is not None:
                profile.location = location if location else ""
            if phone is not None:
                profile.contact = phone if phone else ""
            if website is not None:
                profile.website = website if website else ""
            if description is not None:
                profile.bio = description if description else ""
            db.add(profile)
            
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