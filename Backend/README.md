# College Management Backend

FastAPI backend for a College Management System. This project is the improved `APP` version of the earlier reference backend. It keeps core college-management functionality in `CMS_BASICS`, optional/extra functionality in `CMS_extras`, and shared infrastructure in `Utils`.

## What It Does

The backend provides APIs for:

- Authentication and user management
- Students, teachers, staff, admissions, courses, subjects
- Attendance, fees, marks, reports, dashboard summaries
- Meetings, participants, and meeting messages

After login, the backend also returns a role-specific `dashboard` payload so the frontend can render the first screen immediately without waiting for separate dashboard calls.

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy ORM
- MySQL via PyMySQL
- Pydantic / pydantic-settings
- JWT authentication
- Passlib bcrypt password hashing

## Project Structure

```text
D:\CMS\Backend
|-- MainApplication.py
|-- requirements.txt
|-- requirement.txt
|-- .env.example
|-- APP
|   |-- CMS_BASICS
|   |   |-- Admission
|   |   |-- Attendance
|   |   |-- Course
|   |   |-- Login_resister
|   |   |-- Marks
|   |   |-- Reports
|   |   |-- Staff
|   |   |-- Student
|   |   |-- Subject
|   |   |-- Teacher
|   |   |-- dashbordbyusers
|   |   `-- fees
|   |-- CMS_extras
|   |   |-- ChatBot
|   |   `-- Communication
|   |       |-- Meeting
|   |       `-- Messages
|   `-- Utils
|       |-- Config
|       `-- Database
`-- docs
```

## Setup

Create and activate a virtual environment if needed:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a local `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Update the MySQL settings in `.env`:

```env
DB_URL=jdbc:mysql://localhost:3306/collegemanagement_system
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
```

Make sure the database exists:

```sql
CREATE DATABASE collegemanagement_system;
```

## Run

```powershell
.\.venv\Scripts\python.exe MainApplication.py
```

The server listens on `0.0.0.0:8000`, which means it accepts connections on all network interfaces. In a browser, use:

- `http://localhost:8000/health`
- `http://127.0.0.1:8000/health`
- `http://YOUR_LAN_IP:8000/health`

API docs:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Login And Dashboard

Login endpoint:

```http
POST /api/auth/login
```

Request:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response includes auth data plus dashboard data:

```json
{
  "token": "...",
  "issuedAt": "2026-04-22T...",
  "userId": 1,
  "username": "admin",
  "email": "admin@college.com",
  "role": "Admin",
  "studentId": null,
  "dashboard": {
    "type": "admin",
    "summary": {}
  }
}
```

The dashboard payload depends on role:

- `Admin`: global college summary.
- `Staff`: staff profile plus global summary.
- `Student`: student profile, attendance stats, fee stats, recent attendance, recent fees, pending fees, recent marks.
- `Teacher`: teacher profile, assigned courses, assigned subjects, student counts by assigned course.

## Main API Groups

Most endpoints require a Bearer token from login.

```text
/api/auth
/api/users
/api/courses
/api/subjects
/api/students
/api/admissions
/api/attendance
/api/fees
/api/marks
/api/staff
/api/teachers
/api/dashboard
/api/reports
/api/meetings
```

See [docs/API_OVERVIEW.md](docs/API_OVERVIEW.md) for the endpoint list.

## Important Design Notes

The project uses a layered pattern:

```text
Controller -> Service -> Repository -> SQLAlchemy Model -> Database
       DTO/schema objects carry request and response data
```

This keeps HTTP routing, business logic, and database access separate. That makes modules easier to test, modify, and reason about.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full explanation.

## Configuration

Configuration is read from `.env` by `APP/Utils/Config/AppConfig.py`.

Important variables:

```env
SERVER_PORT=8000
DB_URL=jdbc:mysql://localhost:3306/collegemanagement_system
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
JWT_SECRET=change-this-secret-key-change-this-secret-key
CORS_ALLOWED_ORIGIN_PATTERNS=*
BOOTSTRAP_ADMIN_ENABLED=true
BOOTSTRAP_SAMPLE_DATA_ENABLED=true
```

Do not commit `.env`. It contains secrets. Use `.env.example` as the shared template.

## Verification Commands

Syntax check:

```powershell
python -B -m py_compile MainApplication.py
```

Import check:

```powershell
.\.venv\Scripts\python.exe -B -c "import MainApplication; print(MainApplication.app.title)"
```

Health check after server starts:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## More Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Overview](docs/API_OVERVIEW.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [System Requirements](docs/SYSTEM_REQUIREMENTS.md)
