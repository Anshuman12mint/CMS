from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Course.Course import Course
from APP.CMS_BASICS.Course.CourseDTO import CourseDTO
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class CourseService:
    def __init__(self, session: Session, courseRepository: CourseRepository) -> None:
        self.session = session
        self.courseRepository = courseRepository

    def getAllCourses(self) -> list[CourseDTO]:
        return [self.toDto(course) for course in self.courseRepository.findAll()]

    def getCourse(self, courseCode: str) -> CourseDTO:
        return self.toDto(self.findCourse(courseCode))

    def createCourse(self, request: CourseDTO) -> CourseDTO:
        Validators.requireText(request.courseCode, "courseCode")
        Validators.requireText(request.courseName, "courseName")
        Validators.require(not self.courseRepository.existsById(request.courseCode.strip()), "Course already exists")

        course = Course()
        course.courseCode = Helpers.trimToNull(request.courseCode)  # type: ignore[assignment]
        course.courseName = Helpers.trimToNull(request.courseName)  # type: ignore[assignment]
        course.courseDescription = Helpers.trimToNull(request.courseDescription)
        return self.toDto(self.courseRepository.save(course))

    def updateCourse(self, courseCode: str, request: CourseDTO) -> CourseDTO:
        course = self.findCourse(courseCode)
        Validators.requireText(request.courseName, "courseName")
        course.courseName = Helpers.trimToNull(request.courseName)  # type: ignore[assignment]
        course.courseDescription = Helpers.trimToNull(request.courseDescription)
        return self.toDto(self.courseRepository.save(course))

    def deleteCourse(self, courseCode: str) -> None:
        self.courseRepository.delete(self.findCourse(courseCode))

    def findCourse(self, courseCode: str | None) -> Course:
        course = self.courseRepository.findById(courseCode)
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return course

    def toDto(self, course: Course) -> CourseDTO:
        return CourseDTO(
            courseCode=course.courseCode,
            courseName=course.courseName,
            courseDescription=course.courseDescription,
        )
