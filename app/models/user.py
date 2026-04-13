from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr


class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = Field(default="")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_profile: Optional["StudentProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    admin_profile: Optional["AdminProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    company_profile: Optional["CompanyProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    applications: list[Application] = Relationship(back_populates="user")

class ApplicationBase(SQLModel):
    userId: int = Field(index=True, foreign_key="user.id")#add foreign key
    programmeId: int = Field(index=True, foreign_key="programme.id")#add foreign key
    status: str = Field(index=True)
    
class Application(ApplicationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    programme: Optional[Programme] = Relationship(back_populates="applications")
    user: Optional[User] = Relationship(back_populates="applications")



class ProgrammeBase(SQLModel):
    title: str = Field(index=True, unique=True)
    companyId: int = Field(index=True, foreign_key="company.id")#add foreign key
    academicYear: int = Field(index=True)
    credits: int = Field(index=True)
    keywords: list[str] = Field(default=[])
    compensation: str = Field(index=True)
    

class Programme(ProgrammeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    applications: list[Application] = Relationship(back_populates="programme")
    company: Optional["Company"] = Relationship(back_populates="programmes")


class CompanyBase(SQLModel):
    name: str = Field(index=True, unique=True)

class Company(CompanyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    programmes: list[Programme] = Relationship(back_populates="company")

class ProfileBase(SQLModel):
    contact: str = Field(index=True)
    bio: str = Field(index=True)
    profilePicture: str = Field(index=True)

class StudentProfile(ProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(index=True, foreign_key="user.id", unique=True)#add foreign key
    resume: str = Field(index=True)
    user: Optional["User"] = Relationship(back_populates="student_profile")

class AdminProfile(ProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(index=True, foreign_key="user.id", unique=True)#add foreign key
    user: Optional["User"] = Relationship(back_populates="admin_profile")

class CompanyProfile(ProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(index=True, foreign_key="user.id", unique=True)#add foreign key
    location: str = Field(index=True)
    website: str = Field(index=True)
    user: Optional["User"] = Relationship(back_populates="company_profile")
