# 🧠 Project Management System (FastAPI + PostgreSQL)

A **Task and Project Management System** built using **FastAPI** and **PostgreSQL**.  
It includes features like **task creation**, **assignment**, **progress tracking**, **notifications**, **attendance monitoring**, and **productivity tracking** for employees and managers.

---

## 🚀 Features

### 👩‍💼 Manager Features
- Create and manage **projects** and **tasks**
- Assign tasks to employees
- View **project progress dashboards**
- Track **employee performance**
- Manage **attendance**, **leave requests**, and **payroll**
- Receive notifications for task updates and submissions

### 👨‍💻 Employee Features
- View assigned projects and tasks
- Start, pause, or stop tasks (timestamps stored in **IST**)
- Submit work reports
- Receive notifications for new tasks and status updates
- Apply for leaves and submit complaints

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend Framework** | FastAPI |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Authentication** | JWT (via `python-jose` and `passlib`) |
| **Environment Management** | python-dotenv |
| **Date/Time Handling** | pytz, python-dateutil |
| **Data Analysis & Reports** | pandas, reportlab |
| **Deployment Server** | uvicorn |

---

## 🗂 Project Structure

```
Project/
├── core/                 # Database connection, config, and utilities
├── models/               # SQLAlchemy models (User, Task, Attendance, etc.)
├── routers/              # FastAPI route definitions
├── schemas/              # Pydantic schemas for validation
├── services/             # Business logic / helper functions
├── utils/                # Helper modules (timezone, security, etc.)
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (Database, JWT secret, etc.)
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/project-management-system.git
cd project-management-system
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# or
source venv/bin/activate  # On Mac/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Run Database Migrations
```bash
alembic upgrade head
```

### 6️⃣ Start the Server
```bash
uvicorn main:app --reload
```

Your FastAPI app will now be running at:  
👉 **http://127.0.0.1:8000**
