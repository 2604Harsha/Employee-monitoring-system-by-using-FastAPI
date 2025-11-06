# services/alert_service.py
import asyncio
from datetime import timedelta
from sqlalchemy.orm import Session
from core.database import SessionLocal
from utils.timezone import now_ist
from models.user import User
from models.task import Task
from models.tracking import Tracking
from models.attendance import Attendance
from models.notification import Notification


IDLE_THRESHOLD_MINUTES = 30           
IDLE_CHECK_INTERVAL_SECONDS = 60      

DEADLINE_WINDOW_MINUTES = 60 * 6     
DEADLINE_CHECK_INTERVAL_SECONDS = 300 

ANOMALY_LOOKBACK_DAYS = 14           
ANOMALY_DROP_PERCENT = 50.0          
ANOMALY_CHECK_INTERVAL_SECONDS = 1800 

def get_session():
    return SessionLocal()

def _create_notification(db: Session, user_id: int | None, task_id: int | None, title: str, message: str):
    n = Notification(user_id=user_id, task_id=task_id, title=title, message=message)
    db.add(n)
    db.commit()

async def idle_check_loop():
    """
    Detect idle employees. Last activity comes from:
      - latest Tracking.updated_at (if exists)
      - latest Task.updated_at or Task.created_at if updated_at missing
      - Attendance.punch_in (if still punched in and no punch_out) — consider active
    If last_activity older than threshold -> notify employee and manager.
    """
    while True:
        try:
            db = get_session()
            now = now_ist()
            idle_threshold = now - timedelta(minutes=IDLE_THRESHOLD_MINUTES)

            
            users = db.query(User).filter(User.is_active == True).all()
            for u in users:
                
                if u.role and u.role.lower() in ("admin","manager"):
                    continue

                
                last_tracking = db.query(Tracking).filter(Tracking.task_id.isnot(None)).join(Task, Tracking.task_id==Task.id).filter(
                    (Task.assigned_to == u.id) | (Task.created_by == u.id)
                ).order_by(Tracking.updated_at.desc()).first()

                last_task = db.query(Task).filter((Task.assigned_to == u.id) | (Task.created_by == u.id)).order_by(Task.created_at.desc()).first()

                last_att = db.query(Attendance).filter(Attendance.user_id == u.id).order_by(Attendance.date.desc()).first()

                candidates = []
                if last_tracking and last_tracking.updated_at:
                    candidates.append(last_tracking.updated_at)
                if last_task and last_task.created_at:
                    candidates.append(last_task.created_at)
                if last_att and last_att.punch_in:
                    
                    if last_att.punch_out is None:
                        candidates.append(last_att.punch_in)
                    else:
                        
                        candidates.append(last_att.punch_out)

                if not candidates:
                    last_activity = None
                else:
                    last_activity = max(candidates)

                if last_activity is None or last_activity < idle_threshold:
                   
                    exists = db.query(Notification).filter(Notification.user_id == u.id, Notification.title.ilike("%idle%")).order_by(Notification.created_at.desc()).first()
                    create_it = True
                    if exists:
                        
                        if (now - exists.created_at).total_seconds() < IDLE_THRESHOLD_MINUTES * 60:
                            create_it = False

                    if create_it:
                        title = "Idle-time alert"
                        if last_activity:
                            msg = f"No activity detected since {last_activity.isoformat()}. You've been idle for over {IDLE_THRESHOLD_MINUTES} minutes."
                        else:
                            msg = f"No recorded activity found. Please update task progress / punch-in. Idle threshold: {IDLE_THRESHOLD_MINUTES} minutes."
                        _create_notification(db, user_id=u.id, task_id=None, title=title, message=msg)

                        # Also notify manager(s)
                        managers = db.query(User).filter(User.role.ilike("manager")).all()
                        for m in managers:
                            mmsg = f"Employee {u.name} (id: {u.id}) appears idle. Last activity: {last_activity.isoformat() if last_activity else 'No record'}."
                            _create_notification(db, user_id=m.id, task_id=None, title=f"Employee idle: {u.name}", message=mmsg)

            db.close()
        except Exception as exc:
            print("idle_check_loop error:", exc)
        await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS)


async def deadline_check_loop():
    """
    Notify assignees (and optionally managers) when a task is nearing its due_date.
    """
    while True:
        try:
            db = get_session()
            now = now_ist()
            soon = now + timedelta(minutes=DEADLINE_WINDOW_MINUTES)

            
            tasks = db.query(Task).filter(Task.due_date.isnot(None), Task.due_date <= soon, Task.due_date >= now, Task.status.ilike("%completed%") == False).all()
            for t in tasks:
                
                exists = db.query(Notification).filter(Notification.task_id == t.id, Notification.title.ilike("%due%")).order_by(Notification.created_at.desc()).first()
                create_it = True
                if exists and (now - exists.created_at).total_seconds() < DEADLINE_WINDOW_MINUTES * 0.5:  # don't re-alert too often
                    create_it = False

                if create_it:
                    
                    if t.assigned_to:
                        msg = f"Task '{t.title}' is due at {t.due_date.isoformat()}. Please complete or request extension."
                        _create_notification(db, user_id=t.assigned_to, task_id=t.id, title="Task due soon", message=msg)

                    
                    if t.created_by:
                        _create_notification(db, user_id=t.created_by, task_id=t.id, title="Task due soon (created)", message=f"Task '{t.title}' you created is due at {t.due_date.isoformat()}.")

                    managers = db.query(User).filter(User.role.ilike("manager")).all()
                    for m in managers:
                        _create_notification(db, user_id=m.id, task_id=t.id, title=f"Task due soon: {t.title}", message=f"Task '{t.title}' assigned to user_id={t.assigned_to} is due at {t.due_date.isoformat()}.")

            db.close()
        except Exception as exc:
            print("deadline_check_loop error:", exc)
        await asyncio.sleep(DEADLINE_CHECK_INTERVAL_SECONDS)


async def anomaly_check_loop():
    """
    Detect simple performance anomalies:
     - compare completion counts in two windows of equal length inside the lookback window
     - if completion drops by >= ANOMALY_DROP_PERCENT for a user, notify all managers
    """
    while True:
        try:
            db = get_session()
            from datetime import datetime, timedelta
            now = now_ist()
            lookback = timedelta(days=ANOMALY_LOOKBACK_DAYS)
            window = lookback / 2
            end_recent = now
            start_recent = now - window
            end_prev = start_recent
            start_prev = end_prev - window

            
            users = db.query(User).filter(User.is_active == True).all()
            for u in users:
                if u.role and u.role.lower() in ("admin","manager"):
                    continue
                recent_count = db.query(Task).filter(Task.assigned_to == u.id, Task.status.ilike("%completed%"), Task.created_at >= start_recent, Task.created_at <= end_recent).count()
                prev_count = db.query(Task).filter(Task.assigned_to == u.id, Task.status.ilike("%completed%"), Task.created_at >= start_prev, Task.created_at <= end_prev).count()

                
                if prev_count == 0:
                    continue
                drop_pct = (1 - (recent_count / prev_count)) * 100.0 if prev_count > 0 else 0.0
                if drop_pct >= ANOMALY_DROP_PERCENT:
                    
                    managers = db.query(User).filter(User.role.ilike("manager")).all()
                    for m in managers:
                        exists = db.query(Notification).filter(Notification.user_id == m.id, Notification.title.ilike(f"%anomaly%{u.id}%")).order_by(Notification.created_at.desc()).first()
                        create_it = True
                        if exists and (now - exists.created_at).total_seconds() < ANOMALY_CHECK_INTERVAL_SECONDS:
                            create_it = False
                        if create_it:
                            title = f"Performance anomaly: user {u.name} (id:{u.id})"
                            msg = f"Completed tasks dropped from {prev_count} to {recent_count} (~{drop_pct:.1f}% drop) in the last {lookback.days} days."
                            _create_notification(db, user_id=m.id, task_id=None, title=title, message=msg)

            db.close()
        except Exception as exc:
            print("anomaly_check_loop error:", exc)
        await asyncio.sleep(ANOMALY_CHECK_INTERVAL_SECONDS)


async def start_alert_workers():
    asyncio.create_task(idle_check_loop())
    asyncio.create_task(deadline_check_loop())
    asyncio.create_task(anomaly_check_loop())
