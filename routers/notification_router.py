# routers/notification_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from models.notification import Notification
from schemas.notification_schema import NotificationResponse
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=list[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

@router.put("/{nid}/read")
def mark_read(nid: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == nid, Notification.user_id == current_user.id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"detail": "ok"}

