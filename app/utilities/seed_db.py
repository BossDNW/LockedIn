# app/utilities/seed_db.py

from sqlmodel import Session, select
from app.utilities.security import encrypt_password
from app.models.user import User, StudentProfile, CompanyProfile, AdminProfile, Company

def create_admin_user(db: Session):
    """Create admin user if it doesn't exist"""
    
    admin = db.exec(select(User).where(User.username == "Sally")).first()
    
    if not admin:
        admin_user = User(
            username="Sally",
            email="sally@lockedin.com",
            password=encrypt_password("SallyPass"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create admin profile
        admin_profile = AdminProfile(
            userId=admin_user.id,
            name="Sally Admin",
            contact="sally@lockedin.com",
            bio="System Administrator",
            profilePicture=""
        )
        db.add(admin_profile)
        db.commit()
        
        print("✓ Admin user created (Sally/SallyPass)")
    else:
        print("ℹ Admin user already exists")


def create_company_user(db: Session):
    """Create company user if it doesn't exist"""
    
    company = db.exec(select(User).where(User.username == "GoodEats")).first()
    
    if not company:
        company_user = User(
            username="GoodEats",
            email="goodeats@restaurant.com",
            password=encrypt_password("eatspass"),
            role="company"
        )
        db.add(company_user)
        db.commit()
        db.refresh(company_user)
        
        # Create company record
        company_record = Company(
            id=company_user.id,
            name="GoodEats Restaurant"
        )
        db.add(company_record)
        
        # Create company profile
        company_profile = CompanyProfile(
            userId=company_user.id,
            name="GoodEats Restaurant",
            contact="contact@goodeats.com",
            bio="We serve delicious food made with fresh ingredients!",
            profilePicture="",
            location="123 Main Street, Cityville",
            website="www.goodeats.com"
        )
        db.add(company_profile)
        db.commit()
        
        print("✓ Company user created (GoodEats/eatspass)")
    else:
        print("ℹ Company user already exists")


def create_student_user(db: Session):
    """Create student user if it doesn't exist"""
    
    student = db.exec(select(User).where(User.username == "bob")).first()
    
    if not student:
        student_user = User(
            username="bob",
            email="bob.student@university.com",
            password=encrypt_password("bobpass"),
            role="student"
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)
        
        # Create student profile
        student_profile = StudentProfile(
            userId=student_user.id,
            name="Bob Student",
            contact="bob@student.com",
            bio="Computer Science student passionate about programming and looking for internship opportunities",
            profilePicture="",
            resume=""
        )
        db.add(student_profile)
        db.commit()
        
        print("✓ Student user created (bob/bobpass)")
    else:
        print("ℹ Student user already exists")


def seed_database(db: Session):
    """Seed all necessary data"""
    print("\n🔧 Seeding database with default users...")
    create_admin_user(db)
    create_company_user(db)
    create_student_user(db)
    print("✅ Database seeding complete!\n")