import asyncio
from fastapi import FastAPI
from core.database import Base, engine
from routers import user_router, role_router, monitoring_router, productivity_router,attendance_router,leave_router,task_router,tracking_router,notification_router,reporting_router,alerts_router
from models import user,leave, attendance,task,tracking,project,notification
from services.alert_service import start_alert_workers


Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management System with Authentication")

app.include_router(user_router.router)
# app.include_router(role_router.router)

app.include_router(attendance_router.router)
app.include_router(leave_router.router)
app.include_router(task_router.router)
app.include_router(tracking_router.router)
app.include_router(monitoring_router.router)
app.include_router(productivity_router.router)
app.include_router(notification_router.router)
app.include_router(reporting_router.router)
app.include_router(alerts_router.router)

@app.on_event("startup")
async def startup_event():
    # previous background workers
    loop = asyncio.get_event_loop()
    # start notification/alert workers
    await start_alert_workers()