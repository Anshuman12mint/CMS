# Architecture

## Goal

This backend is structured as a maintainable College Management System. The old reference code was converted into the new `APP` package while preserving behavior and splitting the system into clearer ownership areas.

## High-Level Layout

```text
APP
|-- CMS_BASICS       Core college-management modules
|-- CMS_extras       Optional/extra modules like meetings and chat
`-- Utils            Shared infrastructure used by both
```

`CMS_BASICS` contains features that are part of the normal CMS workflow: students, teachers, staff, courses, subjects, admissions, attendance, fees, marks, reports, users, authentication, and dashboards.

`CMS_extras` contains extra capabilities that are useful but not required for the basic academic records flow, such as meetings and messages.

`Utils` contains shared services: configuration, security, database setup, bootstrap data, helpers, and validators.

## Layered Module Pattern

Most modules follow this pattern:

```text
Controller.py   HTTP routes and FastAPI dependencies
Service.py      Business rules, validation, orchestration
Repository.py   SQLAlchemy database queries
DTO.py          Request/response shape
Model.py        SQLAlchemy mapped database table
```

Example for attendance:

```text
AttendanceController -> AttendanceService -> AttendanceRepository -> Attendance model -> database
```

This separation is intentional:

- Controllers stay thin and only handle HTTP concerns.
- Services contain the real business behavior.
- Repositories isolate query details.
- DTOs stop database models from leaking directly into API contracts.
- Models describe database tables.

## Startup Flow

```mermaid
flowchart TD
    A["Run MainApplication.py"] --> B["createApp()"]
    B --> C["configureSecurity(app)"]
    C --> D["include all routers"]
    D --> E["FastAPI lifespan startup"]
    E --> F["initializeDatabase()"]
    F --> G["import SQLAlchemy models"]
    G --> H["create missing tables"]
    H --> I["Bootstrap admin user"]
    I --> J["Bootstrap sample data if enabled"]
    J --> K["Server ready"]
```

`MainApplication.py` is the composition root. It imports all routers, configures CORS/security, starts database initialization, and exposes the FastAPI `app`.

## Authentication Flow

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as AuthController
    participant Auth as AuthService
    participant DB as Database
    participant Dash as LoginDashboardService

    UI->>API: POST /api/auth/login
    API->>Auth: login(username, password)
    Auth->>DB: find user by username
    Auth->>Auth: verify bcrypt password
    Auth->>Auth: generate JWT
    Auth->>Dash: get role-specific dashboard
    Dash->>DB: read essential dashboard data
    Auth-->>UI: token, user fields, dashboard
```

The login response includes dashboard data because the frontend needs useful first-screen data immediately after login. This avoids a second request before the UI can render the dashboard.

## Dashboard Strategy

There are two dashboard paths:

```text
GET /api/dashboard
```

Returns the global dashboard summary for authenticated users.

```text
POST /api/auth/login
```

Returns authentication data plus role-specific dashboard data.

Why both exist:

- Login dashboard improves first-load speed.
- `/api/dashboard` remains useful for refresh, reload, or admin dashboard pages.
- Role-specific dashboard logic is centralized in `LoginDashboardService`.

Role-specific login dashboard:

- Admin: global totals and recent admissions.
- Staff: staff profile, if matched by email, plus global totals.
- Student: own profile, attendance, fees, pending fees, marks.
- Teacher: own profile, assigned courses, assigned subjects, students by assigned course.

## Security

Security is configured in `APP/Utils/Config/SecurityConfig.py`.

Main responsibilities:

- Password hashing with bcrypt.
- Password verification during login.
- JWT bearer authentication.
- Role checks through `requireRoles`.
- CORS middleware.
- Normalized error responses for HTTP errors.

Most routers depend on `getCurrentUser`, so they require a valid Bearer token:

```http
Authorization: Bearer <token>
```

Admin-only endpoints use `requireRoles("Admin")`.

## Database

Database setup lives in `APP/Utils/Database/DatabaseConfig.py`.

Responsibilities:

- Create the SQLAlchemy base class.
- Create the SQLAlchemy engine.
- Create sessions.
- Import all model classes.
- Create missing tables on startup.

Configuration comes from `.env`, read by `APP/Utils/Config/AppConfig.py`.

The old JDBC-style MySQL URL is accepted:

```env
DB_URL=jdbc:mysql://localhost:3306/collegemanagement_system
```

It is converted internally to SQLAlchemy format:

```text
mysql+pymysql://username:password@localhost:3306/collegemanagement_system
```

## Bootstrap Data

Startup runs:

- `BootstrapAdminInitializer`
- `SampleDataInitializer`

The admin initializer creates a default admin account when enabled.

Sample data creates courses, subjects, a teacher, students, users, attendance, fees, and marks when the database is empty and sample data is enabled.

## Naming And ORM Note

The physical folder names match the current project structure, for example:

```text
APP/CMS_BASICS/Student/Student.py
```

SQLAlchemy can confuse a package called `Student` with a mapped class called `Student`. To keep imports aligned with the folder names while avoiding SQLAlchemy class registry collisions, selected ORM classes define an internal `__module__` value such as:

```python
class Student(Base):
    __module__ = "APP.CMS_BASICS.Student.models"
```

This does not rename the class or file. It only gives SQLAlchemy a non-conflicting internal registry path.

## CORS And Network Access

The app runs with:

```python
host="0.0.0.0"
```

That means the server listens on all network interfaces. It is not a browser URL. Use one of these in the browser:

```text
http://localhost:8000
http://127.0.0.1:8000
http://YOUR_LAN_IP:8000
```

CORS is configured through:

```env
CORS_ALLOWED_ORIGIN_PATTERNS=*
```

This allows frontend development servers on any port to call the backend.

## Design Tradeoffs

The code keeps the original Java/Spring-like naming style: `Controller`, `Service`, `Repository`, and `DTO`. This is verbose for Python, but it makes module responsibilities explicit and keeps the conversion close to the reference implementation.

The startup currently uses `Base.metadata.create_all`. This is simple and good for development. For production, a migration tool such as Alembic would be better.

The login dashboard prioritizes frontend speed. If dashboard data becomes large, the service can return a smaller summary and let the frontend fetch deeper sections lazily.
