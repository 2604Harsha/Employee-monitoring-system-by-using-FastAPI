# services/report_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from utils.timezone import now_ist
from models.task import Task
from models.attendance import Attendance
from models.user import User
from models.project import Project
import pandas as pd
from dateutil.relativedelta import relativedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def _normalize_dates(period: str, start_date: date | None, end_date: date | None):
    today = now_ist().date()
    if period == "day":
        s = today
        e = today
    elif period == "week":
        s = today - timedelta(days=today.weekday())  # monday
        e = s + timedelta(days=6)
    elif period == "month":
        s = today.replace(day=1)
        e = s + relativedelta(months=1) - timedelta(days=1)
    elif period == "custom" and start_date and end_date:
        s = start_date
        e = end_date
    else:
        # default to last 7 days
        s = today - timedelta(days=6)
        e = today
    return s, e

def productivity_dataframe(db: Session, period: str="day", start_date: date|None=None, end_date: date|None=None):
    s, e = _normalize_dates(period, start_date, end_date)
    # fetch tasks in range (created or updated within range)
    tasks = db.query(Task).filter(
        Task.created_at >= datetime.combine(s, datetime.min.time()),
        Task.created_at <= datetime.combine(e, datetime.max.time())
    ).all()
    # attendance rows in range
    atts = db.query(Attendance).filter(
        Attendance.date >= datetime.combine(s, datetime.min.time()),
        Attendance.date <= datetime.combine(e, datetime.max.time())
    ).all()

    # build DataFrame for tasks per user & per day
    task_rows = []
    for t in tasks:
        created_date = t.created_at.date() if t.created_at else None
        is_completed = (t.status and t.status.lower() == "completed")
        task_rows.append({
            "date": created_date,
            "user_id": t.assigned_to,
            "user_name": t.assignee.name if t.assignee else None,
            "task_id": t.id,
            "completed": 1 if is_completed else 0
        })

    if task_rows:
        df_tasks = pd.DataFrame(task_rows)
    else:
        df_tasks = pd.DataFrame(columns=["date","user_id","user_name","task_id","completed"])

    # attendance aggregation per user per day
    att_rows = []
    for a in atts:
        att_date = a.date.date() if a.date else None
        att_rows.append({
            "date": att_date,
            "user_id": a.user_id,
            "work_hours": a.work_hours or 0.0
        })
    if att_rows:
        df_att = pd.DataFrame(att_rows)
    else:
        df_att = pd.DataFrame(columns=["date","user_id","work_hours"])

    # group by date & user
    task_grp = df_tasks.groupby(["date","user_id","user_name"]).agg(tasks_assigned=("task_id","nunique"), tasks_completed=("completed","sum")).reset_index()
    att_grp = df_att.groupby(["date","user_id"]).agg(work_hours=("work_hours","sum")).reset_index()

    merged = pd.merge(task_grp, att_grp, how="outer", left_on=["date","user_id"], right_on=["date","user_id"]).fillna(0)
    # ensure user_name column
    if "user_name" not in merged.columns:
        merged["user_name"] = None

    # completion rate
    merged["completion_rate"] = merged.apply(lambda r: (r["tasks_completed"] / r["tasks_assigned"] * 100) if r["tasks_assigned"]>0 else 0.0, axis=1)
    # fill types
    merged["tasks_assigned"] = merged["tasks_assigned"].astype(int)
    merged["tasks_completed"] = merged["tasks_completed"].astype(int)
    merged["work_hours"] = merged["work_hours"].astype(float)
    merged = merged.sort_values(["date","user_id"])
    return merged, s, e

def department_dashboard(db: Session, start_date: date, end_date: date, dept_field: str="department"):
    """
    If you have a department field on user model, group by department.
    dept_field default 'department' but adapt to your schema.
    """
    # try to access user's department attribute; fallback to 'Unknown'
    users = db.query(User).all()
    rows = []
    for u in users:
        dept = getattr(u, dept_field, "Unknown")
        # compute stats
        tasks_assigned = db.query(Task).filter(Task.assigned_to == u.id, Task.created_at >= datetime.combine(start_date, datetime.min.time()), Task.created_at <= datetime.combine(end_date, datetime.max.time())).count()
        tasks_completed = db.query(Task).filter(Task.assigned_to == u.id, Task.status.ilike("%completed%"), Task.created_at >= datetime.combine(start_date, datetime.min.time()), Task.created_at <= datetime.combine(end_date, datetime.max.time())).count()
        work = db.query(Attendance).filter(Attendance.user_id==u.id, Attendance.date>=datetime.combine(start_date, datetime.min.time()), Attendance.date<=datetime.combine(end_date, datetime.max.time())).all()
        total_hours = sum([a.work_hours or 0.0 for a in work])
        rows.append({"department": dept, "user_id": u.id, "user_name": u.name, "tasks_assigned":tasks_assigned, "tasks_completed":tasks_completed, "work_hours": total_hours})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    grouped = df.groupby("department").agg(tasks_assigned=("tasks_assigned","sum"), tasks_completed=("tasks_completed","sum"), work_hours=("work_hours","sum")).reset_index()
    grouped["completion_rate"] = grouped.apply(lambda r: (r["tasks_completed"]/r["tasks_assigned"]*100) if r["tasks_assigned"]>0 else 0.0, axis=1)
    return grouped

def save_dataframe_to_excel(df: pd.DataFrame, filename: str):
    path = os.path.join("exports", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_excel(path, index=False, engine="openpyxl")
    return path

def save_dataframe_to_pdf(df: pd.DataFrame, filename: str, title: str="Report"):
    path = os.path.join("exports", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # simple table PDF using reportlab
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 40, title)
    c.setFont("Helvetica", 10)
    x = 30
    y = height - 60
    row_height = 14
    # header
    for col in df.columns:
        c.drawString(x, y, str(col))
        x += 100
    y -= row_height
    x = 30
    # rows
    for idx, row in df.iterrows():
        for col in df.columns:
            text = str(row[col]) if not pd.isna(row[col]) else ""
            c.drawString(x, y, text[:20])
            x += 100
        y -= row_height
        x = 30
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40
    c.save()
    return path

def ai_suggestions(db: Session, start_date: date, end_date: date, top_n: int=10):
    """
    Simple rule-based suggestions:
    - Low completion rate + high work_hours => suggest time-management training
    - Low work_hours + low completion => under-assigned / needs help
    - High work_hours + high completion => best practices share
    """
    merged, s, e = productivity_dataframe(db, "custom", start_date, end_date)
    suggestions = []
    # aggregate per user
    agg = merged.groupby(["user_id","user_name"]).agg(tasks_assigned=("tasks_assigned","sum"), tasks_completed=("tasks_completed","sum"), work_hours=("work_hours","sum")).reset_index()
    agg["completion_rate"] = agg.apply(lambda r: (r["tasks_completed"]/r["tasks_assigned"]*100) if r["tasks_assigned"]>0 else 0.0, axis=1)
    # produce suggestions
    for _, r in agg.iterrows():
        uid = int(r["user_id"]) if not pd.isna(r["user_id"]) else None
        uname = r["user_name"]
        cr = r["completion_rate"]
        wh = r["work_hours"]
        ta = r["tasks_assigned"]
        if ta == 0:
            continue
        if cr < 40 and wh > 20:
            suggestions.append({"user_id": uid, "user_name": uname, "suggestion": "Time-management training + review task blockers", "reason": f"Low completion {cr:.1f}% despite high hours ({wh}h)"})
        elif cr < 40 and wh < 10:
            suggestions.append({"user_id": uid, "user_name": uname, "suggestion": "Check workload or capability; Mentor assignment", "reason": f"Low completion {cr:.1f}% and low hours ({wh}h)"})
        elif cr > 80 and wh > 30:
            suggestions.append({"user_id": uid, "user_name": uname, "suggestion": "Employee is high-performer — consider rewards/knowledge share", "reason": f"High completion {cr:.1f}% and high hours ({wh}h)"})
    # return top_n
    return suggestions[:top_n]
