from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.routers import templates

router = APIRouter(tags=["Programmes"])

# HTML PAGE ROUTE - Only this remains
@router.get("/programmes", response_class=HTMLResponse)
async def programmes_page(request: Request):
    """Render the programmes page"""
    return templates.TemplateResponse(
        request=request,
        name="programmes.html"
    )