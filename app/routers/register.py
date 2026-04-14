from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, HTTPException
from app.dependencies import SessionDep
from app.models.user import Company, CompanyProfile, StudentProfile, AdminProfile
from app.schemas.auth import SignupRequest
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.models.user import *
from . import router, templates

# View route (loads the page)
@router.get("/register", response_class=HTMLResponse)
async def register_view(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="register.html",
    )

# Action route (performs an action)
@router.post('/register', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def signup_user(request: Request, db: SessionDep, 
    username: str = Form(),
    email: str = Form(),
    role: str = Form(),
    password: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        # Create the user first
        user = auth_service.register_user(username, email, password, role)
        
        # Now create the profile with the user's ID
        try:
            if role == 'company':
                # Create Company entry
                company = Company(name=username)
                db.add(company)
                db.commit()
                db.refresh(company)
                
                # Create CompanyProfile with userId
                comp_profile = CompanyProfile(
                    userId=user.id,
                    name=username,
                    contact="",
                    bio="",
                    profilePicture="",
                    location="",
                    website=""
                )
                db.add(comp_profile)
                db.commit()
                
            elif role == 'student':
                # Create StudentProfile with userId
                stud_profile = StudentProfile(
                    userId=user.id,
                    name=username,
                    contact="",
                    bio="",
                    profilePicture="",
                    resume=""
                )
                db.add(stud_profile)
                db.commit()
                
            else:  # admin
                # Create AdminProfile with userId
                admin_profile = AdminProfile(
                    userId=user.id,
                    name=username,
                    contact="",
                    bio="",
                    profilePicture=""
                )
                db.add(admin_profile)
                db.commit()
                
        except Exception as e:
            # Rollback user creation if profile creation fails
            db.delete(user)
            db.commit()
            flash(request, f"Error creating profile: {e}", "danger")
            return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
        
        flash(request, "Registration completed! Sign in now!", "success")
        return RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        flash(request, "Username or email already exists", "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)