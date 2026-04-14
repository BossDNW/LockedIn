from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models import user
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.routers import templates

router = APIRouter(tags=["Programmes"])

# HTML PAGE ROUTE - Only this remains
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

    return templates.TemplateResponse(
        request=request,
        name="post-programme.html",
        context={"user": user}
    )

@router.post("/post-programme", response_class=HTMLResponse)
async def post_programme(
    db: SessionDep, 
    user: AuthDep,
    email: str = Form(None),
    username: str = Form(None),
    phone: str = Form(None),
    description: str = Form(None),
    # Company-specific fields
    location: str = Form(None),
    website: str = Form(None),
    #Student specific fields
    resume: str = Form(None)
    ):

    return RedirectResponse(url="/profile", status_code=303)