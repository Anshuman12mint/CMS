from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Teacher.TeacherCourseRepository import TeacherCourseRepository
from APP.CMS_BASICS.Teacher.TeacherDTO import TeacherDTO
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Teacher.TeacherService import TeacherService
from APP.CMS_BASICS.Teacher.TeacherSubjectRepository import TeacherSubjectRepository

router = APIRouter(prefix="/api/teachers", tags=["teachers"], dependencies=[Depends(getCurrentUser)])


class CourseAssignmentRequest(BaseModel):
    courseCodes: list[str] = Field(default_factory=list)


class SubjectAssignmentRequest(BaseModel):
    subjectIds: list[int] = Field(default_factory=list)


def getTeacherService(session: Session = Depends(getDbSession)) -> TeacherService:
    return TeacherService(
        session,
        TeacherRepository(session),
        CourseRepository(session),
        SubjectRepository(session),
        TeacherCourseRepository(session),
        TeacherSubjectRepository(session),
    )


@router.get("", response_model=list[TeacherDTO])
def getTeachers(teacherService: TeacherService = Depends(getTeacherService)) -> list[TeacherDTO]:
    return teacherService.getAllTeachers()


@router.get("/{teacherId}", response_model=TeacherDTO)
def getTeacher(teacherId: int, teacherService: TeacherService = Depends(getTeacherService)) -> TeacherDTO:
    return teacherService.getTeacher(teacherId)


@router.post("", response_model=TeacherDTO, status_code=status.HTTP_201_CREATED)
def createTeacher(request: TeacherDTO, teacherService: TeacherService = Depends(getTeacherService)) -> TeacherDTO:
    return teacherService.createTeacher(request)


@router.put("/{teacherId}", response_model=TeacherDTO)
def updateTeacher(teacherId: int, request: TeacherDTO, teacherService: TeacherService = Depends(getTeacherService)) -> TeacherDTO:
    return teacherService.updateTeacher(teacherId, request)


@router.put("/{teacherId}/courses", response_model=TeacherDTO)
def replaceTeacherCourses(teacherId: int, request: CourseAssignmentRequest, teacherService: TeacherService = Depends(getTeacherService)) -> TeacherDTO:
    return teacherService.replaceCourses(teacherId, request.courseCodes)


@router.put("/{teacherId}/subjects", response_model=TeacherDTO)
def replaceTeacherSubjects(teacherId: int, request: SubjectAssignmentRequest, teacherService: TeacherService = Depends(getTeacherService)) -> TeacherDTO:
    return teacherService.replaceSubjects(teacherId, request.subjectIds)


@router.delete("/{teacherId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteTeacher(teacherId: int, teacherService: TeacherService = Depends(getTeacherService)) -> Response:
    teacherService.deleteTeacher(teacherId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
