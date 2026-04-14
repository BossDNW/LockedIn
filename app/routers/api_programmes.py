from fastapi import APIRouter, Query, HTTPException
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.services.programme_service import ProgrammeService
from app.repositories.programme import ProgrammeRepository
from typing import Optional

router = APIRouter(tags=["API Programmes"])

@router.get("/programmes/search")
async def search_programmes(
    db: SessionDep,
    user: AuthDep,
    q: str = Query(default="", description="Search query"),
    academic_year: Optional[int] = Query(default=None, description="Filter by academic year"),
    credits: Optional[int] = Query(default=None, description="Filter by credits"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page")
):
    """Search and filter programmes"""
    programme_repo = ProgrammeRepository(db)
    programme_service = ProgrammeService(programme_repo)
    
    programmes, pagination = programme_service.search_programmes(
        query=q,
        academic_year=academic_year,
        credits=credits,
        page=page,
        limit=limit
    )
    
    results = []
    for prog in programmes:
        results.append({
            "id": prog.id,
            "title": prog.title,
            "company_name": prog.company.name if prog.company else "",
            "company_location": prog.company.company_profile.location if prog.company and prog.company.company_profile else "",
            "academic_year": prog.academicYear,
            "credits": prog.credits,
            "keywords": prog.keywords,
            "compensation": prog.compensation,
            "schedule": prog.schedule,
            "work_site": prog.workSite,
            "description": getattr(prog, 'description', '')
        })
    
    return {
        "data": results,
        "pagination": {
            "current_page": pagination.page,
            "total_pages": pagination.total_pages,
            "total_count": pagination.total_count,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "next_page": pagination.next_num if pagination.has_next else None,
            "prev_page": pagination.prev_num if pagination.has_prev else None
        }
    }

@router.get("/programmes/{programme_id}")
async def get_programme_detail(
    db: SessionDep,
    user: AuthDep,
    programme_id: int
):
    """Get detailed information about a specific programme"""
    programme_repo = ProgrammeRepository(db)
    programme_service = ProgrammeService(programme_repo)
    
    programme = programme_service.get_programme_details(programme_id)
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    
    return {
        "id": programme.id,
        "title": programme.title,
        "company_name": programme.company.name if programme.company else "",
        "company_location": programme.company.company_profile.location if programme.company and programme.company.company_profile else "",
        "academic_year": programme.academicYear,
        "credits": programme.credits,
        "keywords": programme.keywords,
        "compensation": programme.compensation,
        "schedule": programme.schedule,
        "work_site": programme.workSite,
        "description": getattr(programme, 'description', 'No description available.')
    }

@router.get("/programmes/filters/options")
async def get_filter_options(
    db: SessionDep,
    user: AuthDep
):
    """Get available filter options"""
    programme_repo = ProgrammeRepository(db)
    programme_service = ProgrammeService(programme_repo)
    
    return programme_service.get_filter_options()