from app.repositories.candidate import CandidateRepository
from typing import Optional, Tuple, List
from app.utilities.pagination import Pagination

class CandidateService:
    def __init__(self, candidate_repo: CandidateRepository):
        self.candidate_repo = candidate_repo

    def get_all_students(self, query: str = "", page: int = 1, limit: int = 10) -> Tuple[List, Pagination]:
        """Get all students with pagination"""
        return self.candidate_repo.get_all_students(query, page, limit)

    def get_applications_for_programme(self, programme_id: int) -> List[dict]:
        """Get all applications for a specific programme"""
        return self.candidate_repo.get_applications_for_programme(programme_id)

    def get_all_applications(self, status_filter: str = None, page: int = 1, limit: int = 10) -> Tuple[List[dict], Pagination]:
        """Get all applications with filters"""
        return self.candidate_repo.get_all_applications(status_filter, page, limit)

    def update_application_status(self, application_id: int, new_status: str):
        """Update application status"""
        return self.candidate_repo.update_application_status(application_id, new_status)

    def get_programmes_with_applications(self) -> List[dict]:
        """Get all programmes that have applications"""
        return self.candidate_repo.get_programmes_with_applications()