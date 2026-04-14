from sqlmodel import Session, select, func, or_
from app.models.user import User, Application, Programme, Company
from typing import Optional, Tuple, List
from app.utilities.pagination import Pagination
import logging

logger = logging.getLogger(__name__)

class CandidateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_students(
        self,
        query: str = "",
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[User], Pagination]:
        """Get all students with search"""
        offset = (page - 1) * limit
        
        db_qry = select(User).where(User.role == "student")
        
        if query:
            db_qry = db_qry.where(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%")
                )
            )
        
        count_qry = select(func.count()).select_from(db_qry.subquery())
        total_count = self.db.exec(count_qry).one()
        
        students = self.db.exec(db_qry.offset(offset).limit(limit)).all()
        pagination = Pagination(total_count=total_count, current_page=page, limit=limit)
        
        return students, pagination

    def get_applications_for_programme(self, programme_id: int) -> List[dict]:
        """Get all applications for a specific programme with student details"""
        results = self.db.exec(
            select(Application, User)
            .join(User, Application.userId == User.id)
            .where(Application.programmeId == programme_id)
        ).all()
        
        applications = []
        for app, student in results:
            applications.append({
                "application_id": app.id,
                "student_id": student.id,
                "student_name": student.username,
                "student_email": student.email,
                "status": app.status,
                "applied_date": app.id
            })
        
        return applications

    def get_all_applications(
        self,
        status_filter: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[dict], Pagination]:
        """Get all applications with student and programme details"""
        offset = (page - 1) * limit
        
        db_qry = (
            select(Application, User, Programme, Company)
            .join(User, Application.userId == User.id)
            .join(Programme, Application.programmeId == Programme.id)
            .join(Company, Programme.companyId == Company.id)
        )
        
        if status_filter:
            db_qry = db_qry.where(Application.status == status_filter)
        
        count_qry = select(func.count()).select_from(db_qry.subquery())
        total_count = self.db.exec(count_qry).one()
        
        results = self.db.exec(db_qry.offset(offset).limit(limit)).all()
        
        applications = []
        for app, student, programme, company in results:
            applications.append({
                "application_id": app.id,
                "student_name": student.username,
                "student_email": student.email,
                "programme_title": programme.title,
                "company_name": company.name,
                "status": app.status,
            })
        
        pagination = Pagination(total_count=total_count, current_page=page, limit=limit)
        
        return applications, pagination

    def update_application_status(self, application_id: int, new_status: str) -> Optional[Application]:
        """Update application status (pending/shortlisted/accepted/rejected)"""
        application = self.db.get(Application, application_id)
        if not application:
            return None
        
        application.status = new_status
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_programmes_with_applications(self) -> List[dict]:
        """Get all programmes that have applications"""
        results = self.db.exec(
            select(Programme, Company, func.count(Application.id))
            .join(Company, Programme.companyId == Company.id)
            .outerjoin(Application, Programme.id == Application.programmeId)
            .group_by(Programme.id, Company.id)
        ).all()
        
        programmes = []
        for programme, company, app_count in results:
            programmes.append({
                "id": programme.id,
                "title": programme.title,
                "company_name": company.name,
                "application_count": app_count
            })
        
        return programmes