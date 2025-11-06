from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from utils.security import get_current_user
from utils.timezone import now_ist, today_ist_date
from models.attendance import Attendance
from models.user import User
from utils.timezone import now_ist, utc_to_ist
from schemas.attendance_schema import AttendanceResponse

router = APIRouter(prefix="/attendance", tags=["Attendance & Time Tracking"])

@router.post("/punch_in", response_model=AttendanceResponse)
def punch_in(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = today_ist_date()

    record = db.query(Attendance).filter(
        Attendance.user_id == current_user.id,
        func.date(Attendance.date) == today
    ).first()

    if record:
        raise HTTPException(status_code=400, detail="Already punched in today")

    attendance = Attendance(
        user_id=current_user.id,
        date=now_ist(),
        punch_in=now_ist(),
        is_present=True
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.put("/punch_out", response_model=AttendanceResponse)
def punch_out(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = today_ist_date()
    record = db.query(Attendance).filter(
        Attendance.user_id == current_user.id,
        func.date(Attendance.date) == today
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Punch-in not found for today")

    record.punch_out = now_ist()

    # Convert both times to timezone-aware IST before subtraction
    punch_in_time = utc_to_ist(record.punch_in)
    punch_out_time = utc_to_ist(record.punch_out)

    time_diff = punch_out_time - punch_in_time
    record.work_hours = round(time_diff.total_seconds() / 3600, 2)

    db.commit()
    db.refresh(record)
    return record

@router.get("/", response_model=list[AttendanceResponse])
def get_all_attendance(
    name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can view all attendance records")

    query = db.query(Attendance)
    if name:
        query = query.join(User).filter(User.name.ilike(f"%{name}%"))
    records = query.all()
    return records

@router.get("/me", response_model=list[AttendanceResponse])
def get_my_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(Attendance).filter(Attendance.user_id == current_user.id).all()
    
    # Convert existing UTC times to IST before returning
    for record in records:
        record.date = utc_to_ist(record.date)
        record.punch_in = utc_to_ist(record.punch_in)
        record.punch_out = utc_to_ist(record.punch_out)
    return records