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
        try:
            profile_base = ProfileBase(
                    userId=user.id,
                    name=user.username,
                    contact="",
                    bio="",
                    profilePicture=""
                )
            profile_dict = profile_base.model_dump()
            if role == 'company':
                profile_dict["location"] = ""
                profile_dict["website"] = ""
                comp_profile = CompanyProfile.model_validate(profile_dict)
                db.add(comp_profile)
                db.commit()
                db.refresh(comp_profile)
            elif role == 'student':
                profile_dict["resume"] = ""
                stud_profile = StudentProfile.model_validate(profile_dict)
                db.add(stud_profile)
                db.commit()
                db.refresh(stud_profile)
            else:
                admin_profile = AdminProfile.model_validate(profile_dict)
                db.add(admin_profile)
                db.commit()
                db.refresh(admin_profile)
        except Exception as e:
            db.delete(user)
            db.commit()
            flash(request, f"error: {e}", "danger")
            return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
        
        flash(request, "Registration completed! Sign in now!")
        return RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        flash(request, "Username or email already exists", "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)