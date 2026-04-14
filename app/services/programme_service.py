from app.repositories.programme import ProgrammeRepository
from typing import Optional, Tuple
from app.utilities.pagination import Pagination

class ProgrammeService:
    def __init__(self, programme_repo: ProgrammeRepository):
        self.programme_repo = programme_repo

    def search_programmes(
        self,
        query: str = "",
        academic_year: Optional[int] = None,
        credits: Optional[int] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[list, Pagination]:
        """Search programmes with filters"""
        return self.programme_repo.search_programmes(
            query=query,
            academic_year=academic_year,
            credits=credits,
            page=page,
            limit=limit
        )
    
    def get_programme_details(self, programme_id: int):
        """Get detailed programme information"""
        return self.programme_repo.get_programme_with_details(programme_id)
    
    def get_filter_options(self):
        """Get available filter options"""
        return {
            "academic_years": self.programme_repo.get_unique_academic_years(),
            "credits": self.programme_repo.get_unique_credits()
        }