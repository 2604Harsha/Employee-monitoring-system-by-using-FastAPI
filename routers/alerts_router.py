# routers/alerts_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from utils.security import get_current_user
from models.user import User
from models.notification import Notification
from schemas.notification_schema import NotificationResponse

router = APIRouter(prefix="/alerts", tags=["Alerts & Notifications"])

@router.get("/", response_model=list[NotificationResponse])
def list_my_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # return latest 100 notifications by default
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(200).all()
    return notifs

@router.put("/{nid}/read", status_code=200)
def mark_notification_read(nid: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == nid, Notification.user_id == current_user.id).first()
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    n.is_read = True
    db.commit()
    return {"detail":"ok"}

@router.delete("/{nid}", status_code=200)
def delete_notification(nid: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == nid, Notification.user_id == current_user.id).first()
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    db.delete(n)
    db.commit()
    return {"detail":"deleted"}

@router.get("/unread_count")
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cnt = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).count()
    return {"unread": cnt}
