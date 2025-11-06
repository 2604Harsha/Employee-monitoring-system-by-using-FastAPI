# routers/tracking_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.tracking import Tracking
from models.task import Task
from models.project import Project
from schemas.tracking_schema import TrackingCreate, TrackingResponse, TrackingUpdate
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/tracking", tags=["Tracking"])

@router.post("/", response_model=TrackingResponse)
def create_tracking(payload: TrackingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not (payload.task_id or payload.project_id):
        raise HTTPException(status_code=400, detail="Provide task_id or project_id")

    if payload.task_id:
        t = db.query(Task).filter(Task.id == payload.task_id).first()
        if not t:
            raise HTTPException(404, "Task not found")
    if payload.project_id:
        p = db.query(Project).filter(Project.id == payload.project_id).first()
        if not p:
            raise HTTPException(404, "Project not found")

    tr = Tracking(task_id=payload.task_id, project_id=payload.project_id, status=payload.status, remarks=payload.remarks)
    db.add(tr)
    db.commit()
    db.refresh(tr)

    # sync to task/project
    if tr.task_id:
        t.status = float(tr.status) if tr.status.replace('.','',1).isdigit() else t.status
        t.status = tr.status
        db.commit()
    if tr.project_id:
        p = db.query(Project).filter(Project.id == tr.project_id).first()
        if p:
            p.status = float(tr.status) if tr.status.replace('.','',1).isdigit() else p.status
            p.status = tr.status
            db.commit()

    return tr

@router.put("/{tracking_id}", response_model=TrackingResponse)
def update_tracking(tracking_id: int, data: TrackingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    tr = db.query(Tracking).filter(Tracking.id == tracking_id).first()
    if not tr:
        raise HTTPException(404, "Not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(tr, k, v)
    db.commit()
    db.refresh(tr)

    # sync
    if tr.task_id:
        t = db.query(Task).filter(Task.id == tr.task_id).first()
        if t:
            t.status = tr.progress
            db.commit()
    if tr.assignment_id:
        p = db.query(Project).filter(Project.id == tr.assignment_id).first()
        if p:
            p.status = tr.progress
            db.commit()

    return tr
