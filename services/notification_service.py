# services/notification_service.py
import asyncio
from utils.timezone import now_ist
from datetime import timedelta
from core.database import SessionLocal
from models.task import Task
from models.notification import Notification

CHECK_INTERVAL_SECONDS = 60  # run every minute

async def notification_loop():
    while True:
        try:
            db = SessionLocal()
            now = now_ist()
            soon = now + timedelta(minutes=60)  # tasks due in next 60 minutes
            # pending tasks assigned to someone and due within next hour
            tasks = db.query(Task).filter(Task.assigned_to.isnot(None), Task.status != "Completed", Task.due_date.isnot(None), Task.due_date <= soon, Task.due_date >= now).all()
            for t in tasks:
                # create notification for assignee if not already created in last hour
                exists = db.query(Notification).filter(Notification.task_id == t.id, Notification.user_id == t.assigned_to).order_by(Notification.created_at.desc()).first()
                should_create = True
                if exists:
                    # if a similar notification exists within last 55 minutes skip
                    if (now - exists.created_at).total_seconds() < 55 * 60:
                        should_create = False
                if should_create:
                    msg = f"Task '{t.title}' is due at {t.due_date.isoformat()}. Please finish it."
                    n = Notification(user_id=t.assigned_to, task_id=t.id, title="Task due soon", message=msg)
                    db.add(n)
                    db.commit()
            db.close()
        except Exception as e:
            # simple log; replace with proper logging
            print("Notification loop error:", e)
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
