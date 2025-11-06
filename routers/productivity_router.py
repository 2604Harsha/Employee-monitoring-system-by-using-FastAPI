from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from utils.security import get_current_user
from models.productivity import Productivity
from schemas.productivity_schema import ProductivityCreate, ProductivityUpdate, ProductivityResponse
from models.user import User

router = APIRouter(prefix="/productivity", tags=["Productivity Tracking"])


def calculate_score(productive_time: int, unproductive_time: int) -> float:
    total = productive_time + unproductive_time
    if total == 0:
        return 0.0
    return round((productive_time / total) * 100, 2)


@router.post("/", response_model=ProductivityResponse)
def create_productivity(
    record: ProductivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can create productivity data")

    score = calculate_score(record.productive_time, record.unproductive_time)
    new_record = Productivity(**record.dict(), productivity_score=score)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.put("/{record_id}", response_model=ProductivityResponse)
def update_productivity(
    record_id: int,
    data: ProductivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can update productivity data")

    record = db.query(Productivity).filter(Productivity.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Productivity record not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)
    record.productivity_score = calculate_score(record.productive_time, record.unproductive_time)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_productivity(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can delete productivity data")

    record = db.query(Productivity).filter(Productivity.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Productivity record deleted successfully"}


@router.get("/", response_model=list[ProductivityResponse])
def get_all_productivity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can view all productivity data")
    return db.query(Productivity).all()


@router.get("/me", response_model=list[ProductivityResponse])
def get_my_productivity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() != "employee":
        raise HTTPException(status_code=403, detail="Only employees can access their productivity data")
    return db.query(Productivity).filter(Productivity.user_id == current_user.id).all()
