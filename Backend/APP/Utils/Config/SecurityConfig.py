from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Login_resister.JwtAuthenticationFilter import JwtAuthenticationFilter
from APP.CMS_BASICS.Login_resister.JwtUtil import JwtUtil
from APP.Utils.Config.AppConfig import getSettings
from APP.Utils.Database.DatabaseConfig import getDbSession


bearerScheme = HTTPBearer(auto_error=False)
passwordEncoder = CryptContext(schemes=["bcrypt"], deprecated="auto")


def configureSecurity(app: FastAPI) -> None:
    settings = getSettings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_origin_regex=settings.allowedOriginRegex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization"],
    )

    @app.exception_handler(HTTPException)
    async def httpExceptionHandler(request: Request, exc: HTTPException) -> JSONResponse:  # type: ignore[misc]
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        key = "error" if exc.status_code in {401, 403} else "detail"
        return JSONResponse(status_code=exc.status_code, content={"status": exc.status_code, key: message})


def hashPassword(password: str) -> str:
    return passwordEncoder.hash(password)


def verifyPassword(rawPassword: str, passwordHash: str) -> bool:
    return passwordEncoder.verify(rawPassword, passwordHash)


def getOptionalCurrentUser(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearerScheme),
    session: Session = Depends(getDbSession),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    return JwtAuthenticationFilter(JwtUtil()).authenticate(credentials.credentials.strip(), session)


def getCurrentUser(currentUser=Depends(getOptionalCurrentUser)):
    if currentUser is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required")
    return currentUser


def requireRoles(*roles: str) -> Callable:
    normalizedRoles = {role.strip().upper() for role in roles}

    def dependency(currentUser=Depends(getCurrentUser)):
        role = (currentUser.role or "").strip().upper()
        if role not in normalizedRoles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access is denied")
        return currentUser

    return dependency
