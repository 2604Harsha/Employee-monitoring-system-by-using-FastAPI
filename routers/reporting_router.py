# routers/reporting_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from services.report_service import productivity_dataframe, save_dataframe_to_excel, save_dataframe_to_pdf, department_dashboard, ai_suggestions
from schemas.report_schema import PeriodQuery, ProductivityRow, DashboardResponse, ExportResponse, AISuggestion
from utils.security import get_current_user
from models.user import User
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/reports", tags=["Reporting & Analytics"])

@router.get("/productivity", response_model=list[ProductivityRow])
def get_productivity(period: str = Query("day", enum=["day","week","month","custom"]),
                     start_date: date | None = None,
                     end_date: date | None = None,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """
    Returns productivity rows aggregated by date & user.
    period: day/week/month/custom (use start_date & end_date for custom)
    """
    df, s, e = productivity_dataframe(db, period, start_date, end_date)
    # convert to list of dict for Pydantic
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "date": r["date"].date() if hasattr(r["date"], "date") else r["date"],
            "user_id": int(r["user_id"]) if not pd_is_na(r["user_id"]) else None,
            "user_name": r["user_name"],
            "tasks_assigned": int(r["tasks_assigned"]),
            "tasks_completed": int(r["tasks_completed"]),
            "completion_rate": float(round(r["completion_rate"],2)),
            "work_hours": float(round(r["work_hours"],2)),
        })
    return rows

def pd_is_na(x):
    import pandas as pd
    return pd.isna(x)

@router.get("/department", response_model=DashboardResponse)
def get_department_dashboard(start_date: date | None = None, end_date: date | None = None,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin","manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    # default last month
    if not start_date or not end_date:
        today = datetime.now().date()
        start_date = (today - timedelta(days=30))
        end_date = today
    df = department_dashboard(db, start_date, end_date)
    rows = df.to_dict(orient="records") if not df.empty else []
    return {"title": f"Department dashboard ({start_date} - {end_date})", "rows": rows}

@router.get("/export")
def export_productivity(format: str = Query("excel", enum=["excel","pdf"]),
                        period: str = Query("day", enum=["day","week","month","custom"]),
                        start_date: date | None = None,
                        end_date: date | None = None,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    """
    Export productivity to Excel or PDF. Returns download path on server.
    """
    if current_user.role_name.lower() not in ["admin","manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    df, s, e = productivity_dataframe(db, period, start_date, end_date)
    # small transform
    df_out = df.rename(columns={"date":"Date","user_id":"User ID","user_name":"User Name","tasks_assigned":"Tasks Assigned","tasks_completed":"Tasks Completed","completion_rate":"Completion %","work_hours":"Work Hours"})
    if format == "excel":
        fname = f"productivity_{s}_{e}.xlsx"
        path = save_dataframe_to_excel(df_out, fname)
    else:
        fname = f"productivity_{s}_{e}.pdf"
        path = save_dataframe_to_pdf(df_out, fname, title=f"Productivity {s} to {e}")
    return {"download_path": path}

@router.get("/ai_suggestions", response_model=list[AISuggestion])
def get_ai_suggestions(start_date: date | None = None, end_date: date | None = None,
                       db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_name.lower() not in ["admin","manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not start_date or not end_date:
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        end_date = today
    suggestions = ai_suggestions(db, start_date, end_date)
    # map to AISuggestion
    out = []
    for s in suggestions:
        out.append({"user_id": s["user_id"], "user_name": s["user_name"], "suggestion": s["suggestion"], "reason": s["reason"]})
    return out
