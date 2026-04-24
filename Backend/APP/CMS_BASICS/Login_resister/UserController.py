from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import requireRoles
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Login_resister.UserDTO import UserDTO
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.CMS_BASICS.Login_resister.UserService import UserService

router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[Depends(requireRoles("Admin"))])


class UserMutationRequest(BaseModel):
    username: str
    password: str | None = Field(default=None, min_length=8, max_length=100)
    email: EmailStr
    role: str
    studentId: int | None = None


def getUserService(session: Session = Depends(getDbSession)) -> UserService:
    return UserService(session, UserRepository(session), StudentRepository(session))


@router.get("", response_model=list[UserDTO])
def getUsers(userService: UserService = Depends(getUserService)) -> list[UserDTO]:
    return userService.getUsers()


@router.get("/{userId}", response_model=UserDTO)
def getUser(userId: int, userService: UserService = Depends(getUserService)) -> UserDTO:
    return userService.getUser(userId)


@router.post("", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def createUser(request: UserMutationRequest, userService: UserService = Depends(getUserService)) -> UserDTO:
    return userService.createUser(request)


@router.put("/{userId}", response_model=UserDTO)
def updateUser(userId: int, request: UserMutationRequest, userService: UserService = Depends(getUserService)) -> UserDTO:
    return userService.updateUser(userId, request)


@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteUser(userId: int, userService: UserService = Depends(getUserService)) -> Response:
    userService.deleteUser(userId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
