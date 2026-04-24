from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Student.StudentDTO import StudentDTO
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Student.StudentService import StudentService

router = APIRouter(prefix="/api/students", tags=["students"], dependencies=[Depends(getCurrentUser)])


def getStudentService(session: Session = Depends(getDbSession)) -> StudentService:
    return StudentService(session, StudentRepository(session), CourseRepository(session))


@router.get("", response_model=list[StudentDTO])
def getStudents(courseCode: str | None = Query(default=None), studentService: StudentService = Depends(getStudentService)) -> list[StudentDTO]:
    return studentService.getAllStudents(courseCode)


@router.get("/{studentId}", response_model=StudentDTO)
def getStudent(studentId: int, studentService: StudentService = Depends(getStudentService)) -> StudentDTO:
    return studentService.getStudent(studentId)


@router.post("", response_model=StudentDTO, status_code=status.HTTP_201_CREATED)
def createStudent(request: StudentDTO, studentService: StudentService = Depends(getStudentService)) -> StudentDTO:
    return studentService.createStudent(request)


@router.put("/{studentId}", response_model=StudentDTO)
def updateStudent(studentId: int, request: StudentDTO, studentService: StudentService = Depends(getStudentService)) -> StudentDTO:
    return studentService.updateStudent(studentId, request)


@router.delete("/{studentId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteStudent(studentId: int, studentService: StudentService = Depends(getStudentService)) -> Response:
    studentService.deleteStudent(studentId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
