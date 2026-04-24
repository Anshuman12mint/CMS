from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseDTO import CourseDTO
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Course.CourseService import CourseService
from APP.Utils.Database.DatabaseConfig import getDbSession

router = APIRouter(prefix="/api/courses", tags=["courses"], dependencies=[Depends(getCurrentUser)])


def getCourseService(session: Session = Depends(getDbSession)) -> CourseService:
    return CourseService(session, CourseRepository(session))


@router.get("", response_model=list[CourseDTO])
def getCourses(courseService: CourseService = Depends(getCourseService)) -> list[CourseDTO]:
    return courseService.getAllCourses()


@router.get("/{courseCode}", response_model=CourseDTO)
def getCourse(courseCode: str, courseService: CourseService = Depends(getCourseService)) -> CourseDTO:
    return courseService.getCourse(courseCode)


@router.post("", response_model=CourseDTO, status_code=status.HTTP_201_CREATED)
def createCourse(request: CourseDTO, courseService: CourseService = Depends(getCourseService)) -> CourseDTO:
    return courseService.createCourse(request)


@router.put("/{courseCode}", response_model=CourseDTO)
def updateCourse(courseCode: str, request: CourseDTO, courseService: CourseService = Depends(getCourseService)) -> CourseDTO:
    return courseService.updateCourse(courseCode, request)


@router.delete("/{courseCode}", status_code=status.HTTP_204_NO_CONTENT)
def deleteCourse(courseCode: str, courseService: CourseService = Depends(getCourseService)) -> Response:
    courseService.deleteCourse(courseCode)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
