from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import hashPassword
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Login_resister.User import User
from APP.CMS_BASICS.Login_resister.UserDTO import UserDTO
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class UserService:
    def __init__(self, session: Session, userRepository: UserRepository, studentRepository: StudentRepository) -> None:
        self.session = session
        self.userRepository = userRepository
        self.studentRepository = studentRepository

    def getUsers(self) -> list[UserDTO]:
        return [self.toDto(user) for user in self.userRepository.findAllByOrderByCreatedAtDesc()]

    def getUser(self, userId: int) -> UserDTO:
        return self.toDto(self.findUser(userId))

    def createUser(self, request) -> UserDTO:
        username = Helpers.trimToNull(request.username)
        email = Helpers.trimToNull(request.email)
        role = Validators.normalizeRequiredChoice(request.role, Validators.USER_ROLES, "role")

        Validators.requireText(username, "username")
        Validators.requireText(email, "email")
        Validators.requireText(request.password, "password")

        if self.userRepository.existsByUsername(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if self.userRepository.existsByEmail(email.lower()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        user = User()
        user.username = username
        user.email = email.lower()
        user.role = role
        user.passwordHash = hashPassword(request.password)
        user.student = self.resolveStudent(role, request.studentId)
        user.studentId = user.student.studentId if user.student is not None else None
        return self.toDto(self.userRepository.save(user))

    def updateUser(self, userId: int, request) -> UserDTO:
        user = self.findUser(userId)
        username = Helpers.trimToNull(request.username)
        email = Helpers.trimToNull(request.email)
        role = Validators.normalizeRequiredChoice(request.role, Validators.USER_ROLES, "role")

        Validators.requireText(username, "username")
        Validators.requireText(email, "email")

        if user.username.lower() != username.lower() and self.userRepository.existsByUsername(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if user.email.lower() != email.lower() and self.userRepository.existsByEmail(email.lower()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        user.username = username
        user.email = email.lower()
        user.role = role
        user.student = self.resolveStudent(role, request.studentId)
        user.studentId = user.student.studentId if user.student is not None else None
        if Validators.hasText(request.password):
            user.passwordHash = hashPassword(request.password)
        return self.toDto(self.userRepository.save(user))

    def deleteUser(self, userId: int) -> None:
        self.userRepository.delete(self.findUser(userId))

    def findUser(self, userId: int | None) -> User:
        user = self.userRepository.findById(userId)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def resolveStudent(self, role: str, studentId: int | None) -> Student | None:
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

    def toDto(self, user: User) -> UserDTO:
        return UserDTO(
            userId=user.userId,
            username=user.username,
            email=user.email,
            role=user.role,
            studentId=user.student.studentId if user.student is not None else user.studentId,
            createdAt=user.createdAt,
        )
