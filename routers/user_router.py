from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from core.database import get_db
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import create_user, authenticate_user
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token_data = authenticate_user(db, form_data.username, form_data.password)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return token_data


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/department_team")
def get_department_team(current_user: User = Depends(get_current_user)):
    return {
        "department": current_user.department,
        "team": current_user.team
    }