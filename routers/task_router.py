from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.task import Task
from models.project import Project
from schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from utils.security import get_current_user
from models.user import User
from models.notification import Notification
from utils.timezone import now_ist

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# 🟢 Create Task - Only Admin or Manager
@router.post("/", response_model=TaskResponse)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can create tasks")

    # create task
    task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        created_by=current_user.id,
        assigned_to=task_in.assigned_to
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # create linked project
    proj = Project(
        task_id=task.id,
        project_name=task.title,
        progress=task.progress,
        status=task.status
    )
    db.add(proj)
    db.commit()

    # ✅ create notification for the assigned user
    if task.assigned_to:
        notification = Notification(
            user_id=task.assigned_to,
            task_id=task.id,
            title="New Task Assigned",
            message=f"You have been assigned a new task: '{task.title}'",
            created_at=now_ist()
        )
        db.add(notification)
        db.commit()

    return task


# 🟡 Get Tasks - Admin/Manager see all, Employee sees only their assigned
@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() in ["admin", "manager"]:
        return db.query(Task).all()

    # employee → only their own assigned tasks
    return db.query(Task).filter(Task.assigned_to == current_user.id).all()


# 🟢 Get Task by ID - Employees can only access their own
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    # permission check
    if current_user.role_name.lower() in ["admin", "manager"] or t.assigned_to == current_user.id:
        return t

    raise HTTPException(status_code=403, detail="Not authorized")


# 🟠 Update Task - Only Admin or Manager
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can update tasks")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # update fields
    for k, v in data.dict(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)

    # sync project
    project = db.query(Project).filter(Project.task_id == task.id).first()
    if project:
        project.progress = task.progress
        project.status = task.status
        db.commit()

    # ✅ notify employee about task update
    if task.assigned_to:
        notification = Notification(
            user_id=task.assigned_to,
            task_id=task.id,
            title="Task Updated",
            message=f"Task '{task.title}' has been updated. Current status: {task.status}",
            created_at=now_ist()
        )
        db.add(notification)
        db.commit()

    return task


# 🔴 Delete Task - Only Admin or Manager
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can delete tasks")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}
