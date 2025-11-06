from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schema import UserCreate
from utils.security import hash_password, verify_password, create_access_token

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        contact=user.contact,
        designation=user.designation,
        profile_picture=user.profile_picture,
        department=user.department,
        team=user.team,
        role_name=user.role_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    token = create_access_token({"sub": user.email, "role": user.role_name})
    return {"access_token": token, "token_type": "bearer"}
