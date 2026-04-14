from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="app.html",
        context={
            "user": user
        }
    )