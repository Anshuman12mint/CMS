# Development Guide

## Local Environment

Install dependencies:

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

The standard dependency file is `requirements.txt`. The older `requirement.txt` is still present for compatibility.

Run the app:

```powershell
.\.venv\Scripts\python.exe MainApplication.py
```

Open:

```text
http://localhost:8000/docs
```

## Environment Files

Use `.env.example` as the shared template. Create a private `.env` for local secrets:

```powershell
Copy-Item .env.example .env
```

Never commit `.env`. It contains database credentials and JWT secrets.

## Adding A New Basic CMS Module

Use this structure:

```text
APP/CMS_BASICS/NewModule
|-- NewModule.py
|-- NewModuleDTO.py
|-- NewModuleRepository.py
|-- NewModuleService.py
|-- NewModuleController.py
`-- __init__.py
```

Then:

1. Add the SQLAlchemy model import to `APP/Utils/Database/DatabaseConfig.py`.
2. Add the router import to `MainApplication.py`.
3. Add the router to the `ROUTERS` tuple.
4. Add validation rules to `APP/Utils/Validators.py` if needed.
5. Add endpoint documentation to `docs/API_OVERVIEW.md`.

## Layer Responsibilities

Controller:

- Defines route paths and HTTP methods.
- Creates services through FastAPI dependencies.
- Returns DTOs or dictionaries.

Service:

- Owns business rules.
- Validates required fields.
- Converts model objects to DTOs.
- Coordinates multiple repositories.

Repository:

- Owns SQLAlchemy queries.
- Keeps query logic out of services.
- Provides methods like `findById`, `findAll`, `save`, `delete`, `count`.

DTO:

- Defines API input/output data.
- Uses Pydantic for serialization.

Model:

- Defines table name, columns, relationships.
- Inherits from `Base`.

## Verification

Syntax check:

```powershell
python -B -m py_compile MainApplication.py
```

Import check:

```powershell
.\.venv\Scripts\python.exe -B -c "import MainApplication; print(MainApplication.app.title)"
```

Model registration check:

```powershell
.\.venv\Scripts\python.exe -B -c "from APP.Utils.Database.DatabaseConfig import importModels, Base; importModels(); print(sorted(Base.metadata.tables.keys()))"
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Login check:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/auth/login `
  -ContentType application/json `
  -Body '{"username":"admin","password":"admin123"}'
```

## Troubleshooting

### Browser cannot open `0.0.0.0:8000`

`0.0.0.0` is a bind address, not a browser address. Use:

```text
http://localhost:8000
http://127.0.0.1:8000
http://YOUR_LAN_IP:8000
```

### MySQL access denied

If the error says:

```text
Access denied for user 'root'@'localhost' (using password: NO)
```

then `.env` is missing or `DB_PASSWORD` is empty.

### Unknown database

Create the database:

```sql
CREATE DATABASE collegemanagement_system;
```

### CORS failure from frontend

Check:

```env
CORS_ALLOWED_ORIGIN_PATTERNS=*
```

Restart the backend after changing `.env`.

### SQLAlchemy package/class name collision

Some mapped classes define `__module__` to prevent SQLAlchemy from confusing a package name with a class name. Keep this line when editing those models:

```python
__module__ = "APP.CMS_BASICS.Student.models"
```

This does not change API imports or class names.

## Suggested Future Engineering Improvements

- Add Alembic migrations instead of relying only on `create_all`.
- Add automated tests for auth, dashboard payloads, and CRUD modules.
- Add response models for auth payloads.
- Split secrets per environment: development, staging, production.
- Add structured logging.
- Add pagination for list endpoints.
- Add role-specific authorization rules beyond authentication-only access.
