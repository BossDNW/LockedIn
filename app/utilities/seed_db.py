from sqlmodel import Session, select
from app.utilities.security import encrypt_password
from app.models.user import User, StudentProfile, CompanyProfile, AdminProfile, Company

def create_admin_user(db: Session):
    
    admin = db.exec(select(User).where(User.username == "Sally")).first()
    
    if admin:
        print("ℹ Admin user already exists")
        return admin
    
    admin_user = User(
        username="Sally",
        email="sally@lockedin.com",
        password=encrypt_password("sallypass"),
        role="admin"
    )
    db.add(admin_user)
    db.flush()
    db.refresh(admin_user)
    
    admin_profile = db.exec(
        select(AdminProfile).where(AdminProfile.userId == admin_user.id)
    ).first()
    
    if not admin_profile:
        admin_profile = AdminProfile(
            userId=admin_user.id,
            name="Sally Admin",
            contact="+1(868) 123-4567", 
            bio="System Administrator",
            profilePicture=""
        )
        db.add(admin_profile)
    
    print("✓ Admin user created (Sally/SallyPass)")
    return admin_user


def create_company_user(db: Session):
    
    company = db.exec(select(User).where(User.username == "Microzon")).first()
    
    if company:
        print("ℹ Company user already exists")
        return company
    
    company_user = User(
        username="Microzon", 
        email="microzon@company.com",  
        password=encrypt_password("micropass"),  
        role="company"
    )
    db.add(company_user)
    db.flush()
    db.refresh(company_user)
    
    company_record = db.exec(
        select(Company).where(Company.id == company_user.id)
    ).first()
    
    if not company_record:
        company_record = Company(
            id=company_user.id,
            name="Microzon Technologies" 
        )
        db.add(company_record)
    
    company_profile = db.exec(
        select(CompanyProfile).where(CompanyProfile.userId == company_user.id)
    ).first()
    
    if not company_profile:
        company_profile = CompanyProfile(
            userId=company_user.id,
            name="Microzon Technologies",
            contact="+1(868) 456-7890",  
            bio="Leading technology solutions provider specializing in innovative software development and IT consulting services.",
            profilePicture="",
            location="Port of Spain, Trinidad and Tobago",
            website="www.microzon.com"
        )
        db.add(company_profile)
    
    print("✓ Company user created (Microzon/micropass)")
    return company_user


def create_student_user(db: Session):
    
    student = db.exec(select(User).where(User.username == "bob")).first()
    
    if student:
        print("ℹ Student user already exists")
        return student
    
    student_user = User(
        username="bob",
        email="bob.student@university.com",
        password=encrypt_password("bobpass"),
        role="student"
    )
    db.add(student_user)
    db.flush()
    db.refresh(student_user)
    
    student_profile = db.exec(
        select(StudentProfile).where(StudentProfile.userId == student_user.id)
    ).first()
    
    if not student_profile:
        student_profile = StudentProfile(
            userId=student_user.id,
            name="Bob Student",
            contact="+1(868) 789-0123",  
            bio="Computer Science student passionate about programming and looking for internship opportunities.",
            profilePicture="",
            resume=""
        )
        db.add(student_profile)
    
    print("✓ Student user created (bob/bobpass)")
    return student_user


def seed_database(db: Session):
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