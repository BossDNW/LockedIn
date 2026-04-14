from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.dependencies.session import SessionDep
from . import router


@router.get("/", response_class=RedirectResponse)
async def index_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep
):
    if user_logged_in:
        user = await get_current_user(request, db)
        if user.role == 'admin':
            return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        elif user.role == 'company':
            return RedirectResponse(url="/candidates", status_code=status.HTTP_303_SEE_OTHER)
        else:  # student
            return RedirectResponse(url="/my-applications", status_code=status.HTTP_303_SEE_OTHER)
    
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token", 
        httponly=True,
        samesite="lax",
        secure=False
    )
    return response