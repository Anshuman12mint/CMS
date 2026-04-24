from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Login_resister.AuthService import AuthService
from APP.CMS_BASICS.Login_resister.JwtUtil import JwtUtil
from APP.CMS_BASICS.dashbordbyusers.LoginDashboardService import LoginDashboardService
from APP.Utils.Config.SecurityConfig import requireRoles
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=100)
    email: EmailStr
    role: str
    studentId: int | None = None


def getAuthService(session: Session = Depends(getDbSession)) -> AuthService:
    return AuthService(
        session,
        UserRepository(session),
        StudentRepository(session),
        JwtUtil(),
        LoginDashboardService(session),
    )


@router.post("/login")
def login(request: LoginRequest, authService: AuthService = Depends(getAuthService)) -> dict[str, object]:
    return authService.login(request)


@router.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(requireRoles("Admin"))])
def register(request: RegisterRequest, authService: AuthService = Depends(getAuthService)) -> dict[str, object]:
    return authService.register(request)
