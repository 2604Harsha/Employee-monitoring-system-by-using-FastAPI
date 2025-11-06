from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.monitoring import EmployeeMonitoring
from schemas.monitoring_schema import MonitoringCreate, MonitoringUpdate, MonitoringResponse
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/monitoring", tags=["Employee Monitoring"])


@router.post("/", response_model=MonitoringResponse)
def create_monitoring(
    monitoring: MonitoringCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can create monitoring records")

    new_monitoring = EmployeeMonitoring(**monitoring.dict())
    db.add(new_monitoring)
    db.commit()
    db.refresh(new_monitoring)
    return new_monitoring


@router.put("/{monitoring_id}", response_model=MonitoringResponse)
def update_monitoring(
    monitoring_id: int,
    update_data: MonitoringUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can update monitoring data")

    record = db.query(EmployeeMonitoring).filter(EmployeeMonitoring.id == monitoring_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Monitoring record not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record



@router.delete("/{monitoring_id}")
def delete_monitoring(
    monitoring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can delete monitoring data")

    record = db.query(EmployeeMonitoring).filter(EmployeeMonitoring.id == monitoring_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Monitoring record not found")

    db.delete(record)
    db.commit()
    return {"message": "Monitoring record deleted successfully"}



@router.get("/", response_model=list[MonitoringResponse])
def get_all_monitoring(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only Admin or Manager can view monitoring data")

    return db.query(EmployeeMonitoring).all()


@router.get("/me", response_model=list[MonitoringResponse])
def get_my_monitoring_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_name.lower() != "employee":
        raise HTTPException(status_code=403, detail="Only Employees can access their own data")

    return db.query(EmployeeMonitoring).filter(EmployeeMonitoring.user_id == current_user.id).all()
