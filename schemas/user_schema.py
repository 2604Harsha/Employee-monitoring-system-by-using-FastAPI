from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    email: EmailStr
    contact: str | None = None
    designation: str | None = None
    profile_picture: str | None = None
    department: str | None = None
    team: str | None = None
    role_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        orm_mode = True
