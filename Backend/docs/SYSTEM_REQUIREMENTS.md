# System Requirements

This document describes what is needed to run the College Management Backend locally and what resources are recommended for deployment.

## Software Requirements

Minimum software:

| Requirement | Minimum | Recommended |
| --- | --- | --- |
| Python | 3.11 | 3.11 or newer |
| Package manager | pip | pip with virtual environment |
| Database | MySQL 8.x or MariaDB compatible | MySQL 8.x |
| Operating system | Windows 10/11, Linux, or macOS | Windows 11 or Linux server |
| API server | Uvicorn | Uvicorn behind reverse proxy for production |
| Browser for docs | Any modern browser | Chrome, Edge, Firefox |

Python dependencies are listed in:

```text
requirements.txt
```

Install them with:

```powershell
pip install -r requirements.txt
```

The older `requirement.txt` file is kept for compatibility, but `requirements.txt` is the standard Python filename.

## Python Dependencies

| Package | Purpose |
| --- | --- |
| `fastapi` | API framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM and database access |
| `pydantic` | DTO/request/response validation |
| `pydantic-settings` | `.env` configuration |
| `email-validator` | Email validation for auth/register payloads |
| `pymysql` | MySQL driver |
| `pyjwt` | JWT token creation and validation |
| `passlib[bcrypt]` | Password hashing |
| `bcrypt<4` | Compatible bcrypt backend for passlib |

## Local Development Requirements

Good local development setup:

| Resource | Minimum | Recommended |
| --- | --- | --- |
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB or more |
| Disk | 1 GB free | 5 GB free |
| MySQL storage | 500 MB for test data | 5 GB or more |
| Network | Localhost | LAN access if frontend is on another device |

This backend itself is lightweight. Most local resource usage comes from MySQL, the Python virtual environment, and your IDE.

## Small Deployment Requirements

For a small college demo or internal prototype:

| Component | Minimum | Recommended |
| --- | --- | --- |
| App server CPU | 1 vCPU | 2 vCPU |
| App server RAM | 512 MB | 1-2 GB |
| Database RAM | 1 GB | 2-4 GB |
| App disk | 1 GB | 5 GB |
| Database disk | 5 GB | 20 GB+ |
| Network port | 8000 or proxied HTTP/HTTPS | HTTPS behind proxy |

Recommended process split:

```text
Frontend -> Backend API -> MySQL database
```

For production-like deployment, run the backend and database as separate services.

## Environment Variables

Required:

```env
DB_URL=jdbc:mysql://localhost:3306/collegemanagement_system
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
JWT_SECRET=change-this-secret-key-change-this-secret-key
```

Common optional settings:

```env
SERVER_PORT=8000
CORS_ALLOWED_ORIGIN_PATTERNS=*
JWT_EXPIRATION_MINUTES=120
BOOTSTRAP_ADMIN_ENABLED=true
BOOTSTRAP_SAMPLE_DATA_ENABLED=true
```

Use `.env.example` as the template and keep the real `.env` private.

## Network Requirements

Backend server:

```text
0.0.0.0:8000
```

Browser access from the same machine:

```text
http://localhost:8000
http://127.0.0.1:8000
```

Access from another device on the same network:

```text
http://YOUR_LAN_IP:8000
```

Database port:

```text
3306
```

Only expose MySQL to trusted machines. In most setups, MySQL should not be publicly accessible.

## Runtime Behavior

On startup, the backend:

1. Reads `.env`.
2. Creates the SQLAlchemy database engine.
3. Imports all ORM models.
4. Creates missing tables.
5. Bootstraps admin user if enabled.
6. Bootstraps sample data if enabled and the database is empty.
7. Starts accepting HTTP requests.

Because startup touches the database, the backend needs MySQL credentials to be correct before it can fully start.

## Production Notes

For a production deployment:

- Use a strong `JWT_SECRET`.
- Disable or review `BOOTSTRAP_SAMPLE_DATA_ENABLED`.
- Put Uvicorn behind Nginx, Apache, IIS, or another reverse proxy.
- Use HTTPS.
- Restrict CORS to known frontend origins instead of `*`.
- Use a non-root MySQL user with only the required database permissions.
- Add database backups.
- Add monitoring and log retention.
- Use migrations, preferably Alembic, instead of only `create_all`.

## Quick Checklist

Before running:

- Python installed.
- Virtual environment created.
- Dependencies installed from `requirements.txt`.
- MySQL running.
- Database `collegemanagement_system` created.
- `.env` exists with correct DB credentials.
- Port `8000` is free or `SERVER_PORT` changed.

Run:

```powershell
.\.venv\Scripts\python.exe MainApplication.py
```

Check:

```text
http://localhost:8000/health
http://localhost:8000/docs
```
