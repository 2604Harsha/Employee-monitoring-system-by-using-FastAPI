from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.leave import Leave, LeaveStatus
from models.user import User
from schemas.leave_schema import LeaveCreate, LeaveUpdate, LeaveResponse
from utils.security import get_current_user

router = APIRouter(prefix="/leave", tags=["Leave Management"])

@router.post("/", response_model=LeaveResponse)
def create_leave(
    leave_data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["employee"]:
        raise HTTPException(status_code=403, detail="Only employees can create leave requests")

    leave = Leave(
        user_id=current_user.id,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        reason=leave_data.reason
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave



@router.get("/me", response_model=list[LeaveResponse])
def get_my_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Leave).filter(Leave.user_id == current_user.id).all()



@router.get("/", response_model=list[LeaveResponse])
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Access restricted to Admin or Manager")

    return db.query(Leave).all()



@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave_status(
    leave_id: int,
    update_data: LeaveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Access restricted to Admin or Manager")

    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    leave.status = update_data.status
    db.commit()
    db.refresh(leave)
    return leave



@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Access restricted to Admin or Manager")

    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    db.delete(leave)
    db.commit()
    return {"message": "Leave record deleted successfully"}
