from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, HTTPException
from app.dependencies import SessionDep
from app.models.user import Company, CompanyProfile, StudentProfile, AdminProfile
from app.schemas.auth import SignupRequest
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
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
def signup_user(request:Request, db:SessionDep, 
    username: str = Form(),
    email: str = Form(),
    role : str = Form(),
    password: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        user = auth_service.register_user(username, email, password, role)
        
        # Create profile based on role
        if role == 'student':
            student_profile = StudentProfile(
                userId=user.id,
                contact="",
                bio="",
                profilePicture="",
                resume=""
            )
            db.add(student_profile)
            
        elif role == 'company':
            company_profile = CompanyProfile(
                userId=user.id,
                contact="",
                bio="",
                profilePicture="",
                location="",
                website=""
            )
            db.add(company_profile)
            
            # Also create Company record
            company = Company(
                id=user.id,
                name=username
            )
            db.add(company)
            
        elif role == 'admin':
            admin_profile = AdminProfile(
                userId=user.id,
                contact="",
                bio="",
                profilePicture=""
            )
            db.add(admin_profile)
        
        db.commit()
        flash(request, "Registration completed! Sign in now!")
        return RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        flash(request, "Username or email already exists", "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)