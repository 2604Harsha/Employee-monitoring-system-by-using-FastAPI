# routers/project_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.project import Project
from models.task import Task
from schemas.project_schema import ProjectResponse, ProjectUpdate
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Project).all()

@router.get("/my", response_model=list[ProjectResponse])
def get_my_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Project).join(Task).filter(Task.assigned_to == current_user.id).all()

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(project, k, v)
    db.commit()
    db.refresh(project)

    # Sync back to task
    task = db.query(Task).filter(Task.id == project.task_id).first()
    if task:
        if project.progress is not None:
            task.progress = project.progress
        if project.status is not None:
            task.status = project.status
        db.commit()
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "deleted"}
