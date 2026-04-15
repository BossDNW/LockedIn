# app/utilities/seed_db.py

from sqlmodel import Session, select
from app.utilities.security import encrypt_password
from app.models.user import User, StudentProfile, CompanyProfile, AdminProfile, Company

def create_admin_user(db: Session):
    """Create admin user if it doesn't exist"""
    
    # Check if admin already exists
    admin = db.exec(select(User).where(User.username == "Sally")).first()
    
    if not admin:
        admin_user = User(
            username="Sally",
            email="sally@lockedin.com",
            password=encrypt_password("sallypass"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create admin profile
        admin_profile = AdminProfile(
            userId=admin_user.id,
            name="Sally Admin",
            contact="+1(868)555-1234",
            bio="System Administrator",
            profilePicture=""
        )
        db.add(admin_profile)
        db.commit()
        
        print("✓ Admin user created (Sally/sallypass)")
    else:
        print("ℹ Admin user already exists")


def create_company_user(db: Session):
    """Create company user if it doesn't exist"""
    
    company = db.exec(select(User).where(User.username == "Microzon")).first()
    
    if company:
        print("ℹ Company user already exists")
        return company
    
    # Create company user
    company_user = User(
        username="GoodEats",
        email="goodeats@restaurant.com",
        password=encrypt_password("eatspass"),
        role="company"
    )
    db.add(company_user)
    db.flush()  # Flush to get the ID without committing
    db.refresh(company_user)
    
    # Check if company record already exists
    company_record = db.exec(
        select(Company).where(Company.id == company_user.id)
    ).first()
    
    if not company_record:
        company_record = Company(
            id=company_user.id,
            name="GoodEats Restaurant"
        )
        db.add(company_record)
    
    # Check if company profile already exists
    company_profile = db.exec(
        select(CompanyProfile).where(CompanyProfile.userId == company_user.id)
    ).first()
    
    if not company_profile:
        company_profile = CompanyProfile(
            userId=company_user.id,
            name="GoodEats Restaurant",
            contact="+1(868)555-5678",
            bio="We serve delicious food made with fresh ingredients!",
            profilePicture="",
            location="123 Main Street, Cityville",
            website="www.goodeats.com"
        )
        db.add(company_profile)
    
    print("✓ Company user created (GoodEats/eatspass)")
    return company_user


def create_student_user(db: Session):
    """Create student user if it doesn't exist"""
    
    # Check if student already exists
    student = db.exec(select(User).where(User.username == "bob")).first()
    
    if student:
        print("ℹ Student user already exists")
        return student
    
    # Create student user
    student_user = User(
        username="bob",
        email="bob.student@university.com",
        password=encrypt_password("bobpass"),
        role="student"
    )
    db.add(student_user)
    db.flush()  # Flush to get the ID without committing
    db.refresh(student_user)
    
    # Check if student profile already exists
    student_profile = db.exec(
        select(StudentProfile).where(StudentProfile.userId == student_user.id)
    ).first()
    
    if not student_profile:
        student_profile = StudentProfile(
            userId=student_user.id,
            name="Bob Student",
            contact="+1(868)555-9012",
            bio="Computer Science student passionate about programming",
            profilePicture="",
            resume=""
        )
        db.add(student_profile)
    
    print("✓ Student user created (bob/bobpass)")
    return student_user


def seed_database(db: Session):
    """Seed all necessary data"""
    print("\n🔧 Seeding database with default users...")
    
    try:
        create_admin_user(db)
        create_company_user(db)
        create_student_user(db)
        
        db.commit()
        print("✅ Database seeding complete!\n")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise