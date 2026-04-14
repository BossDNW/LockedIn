from sqlmodel import Session, select, func, or_
from app.models.user import Programme, Company
from typing import Optional, Tuple, List
from app.utilities.pagination import Pagination
import logging

logger = logging.getLogger(__name__)

class ProgrammeRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_programmes(
        self, 
        query: str = "", 
        academic_year: Optional[int] = None,
        credits: Optional[int] = None,
        page: int = 1, 
        limit: int = 10
    ) -> Tuple[List[Programme], Pagination]:
        """Search programmes with filters"""
        offset = (page - 1) * limit
        
        # Base query with join to Company
        db_qry = select(Programme).join(Company, Programme.companyId == Company.id)
        
        # Apply search query (title or company name)
        if query:
            db_qry = db_qry.where(
                or_(
                    Programme.title.ilike(f"%{query}%"),
                    Company.name.ilike(f"%{query}%")
                )
            )
        
        # Apply academic year filter
        if academic_year:
            db_qry = db_qry.where(Programme.academicYear == academic_year)
        
        # Apply credits filter
        if credits:
            db_qry = db_qry.where(Programme.credits == credits)
        
        # Get count
        count_qry = select(func.count()).select_from(db_qry.subquery())
        total_count = self.db.exec(count_qry).one()
        
        # Get paginated results
        programmes = self.db.exec(
            db_qry.offset(offset).limit(limit)
        ).all()
        
        pagination = Pagination(
            total_count=total_count, 
            current_page=page, 
            limit=limit
        )
        
        return programmes, pagination
    
    def get_programme_with_details(self, programme_id: int) -> Optional[Programme]:
        """Get a single programme with company details"""
        return self.db.exec(
            select(Programme)
            .join(Company, Programme.companyId == Company.id)
            .where(Programme.id == programme_id)
        ).one_or_none()
    
    def get_unique_academic_years(self) -> List[int]:
        """Get all unique academic years for filter dropdown"""
        result = self.db.exec(
            select(Programme.academicYear).distinct().order_by(Programme.academicYear.desc())
        ).all()
        return list(result)
    
    def get_unique_credits(self) -> List[int]:
        """Get all unique credit values for filter dropdown"""
        result = self.db.exec(
            select(Programme.credits).distinct().order_by(Programme.credits)
        ).all()
        return list(result)