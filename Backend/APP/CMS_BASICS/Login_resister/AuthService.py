from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Login_resister.JwtUtil import JwtUtil
from APP.CMS_BASICS.dashbordbyusers.LoginDashboardService import LoginDashboardService
from APP.Utils.Config.AppConfig import utcNow
from APP.Utils.Config.SecurityConfig import hashPassword, verifyPassword
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Login_resister.User import User
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class AuthService:
    def __init__(
        self,
        session: Session,
        userRepository: UserRepository,
        studentRepository: StudentRepository,
        jwtUtil: JwtUtil,
        loginDashboardService: LoginDashboardService | None = None,
    ) -> None:
        self.session = session
        self.userRepository = userRepository
        self.studentRepository = studentRepository
        self.jwtUtil = jwtUtil
        self.loginDashboardService = loginDashboardService

    def register(self, request) -> dict[str, object]:
        username = Helpers.trimToNull(request.username)
        email = Helpers.trimToNull(request.email)
        role = Validators.normalizeRequiredChoice(request.role, Validators.USER_ROLES, "role")

        Validators.requireText(username, "username")
        Validators.requireText(request.password, "password")
        Validators.requireText(email, "email")

        if self.userRepository.existsByUsername(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if self.userRepository.existsByEmail(email.lower()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        student = self.resolveStudentLink(role, request.studentId)
        user = User()
        user.username = username
        user.passwordHash = hashPassword(request.password)
        user.email = email.lower()
        user.role = role
        user.student = student
        user.studentId = student.studentId if student is not None else None
        saved = self.userRepository.save(user)
        token = self.jwtUtil.generateToken(saved.username, saved.role)
        return self.authPayload(saved, token)

    def login(self, request) -> dict[str, object]:
        Validators.requireText(request.username, "username")
        Validators.requireText(request.password, "password")

        user = self.userRepository.findByUsername(request.username.strip())
        if user is None or not verifyPassword(request.password, user.passwordHash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        token = self.jwtUtil.generateToken(user.username, user.role)
        return self.authPayload(user, token, includeDashboard=True)

    def authPayload(self, user: User, token: str, includeDashboard: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "token": token,
            "issuedAt": utcNow().isoformat(),
            "userId": user.userId,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "studentId": user.student.studentId if user.student is not None else user.studentId,
        }
        if includeDashboard and self.loginDashboardService is not None:
            payload["dashboard"] = self.loginDashboardService.getDashboardForUser(user)
        return payload

    def resolveStudentLink(self, role: str, studentId: int | None) -> Student | None:
        if role.lower() == "student":
            Validators.require(studentId is not None, "studentId is required for Student role")
        elif studentId is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="studentId can only be linked to Student role")

        if studentId is None:
            return None
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student
