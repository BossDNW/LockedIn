from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.routers import templates
from app.models.user import Application, Programme, Company
from sqlmodel import select

router = APIRouter(tags=["My Applications"])

# HTML PAGE - View my applications (ONLY for students)
@router.get("/my-applications", response_class=HTMLResponse)
async def my_applications_page(request: Request, user: AuthDep):
    """Render the my applications page - ONLY STUDENTS CAN ACCESS"""
    if user.role != 'student':
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only students can view their applications."
        )
    
    return templates.TemplateResponse(
        request=request,
        name="my_applications.html",
        context={"user": user}
    )