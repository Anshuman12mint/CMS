from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Subject.Subject import Subject
from APP.CMS_BASICS.Subject.SubjectDTO import SubjectDTO
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class SubjectService:
    def __init__(self, session: Session, subjectRepository: SubjectRepository, courseRepository: CourseRepository) -> None:
        self.session = session
        self.subjectRepository = subjectRepository
        self.courseRepository = courseRepository

    def getAllSubjects(self, courseCode: str | None) -> list[SubjectDTO]:
        subjects = self.subjectRepository.findAll() if courseCode is None or courseCode.strip() == "" else self.subjectRepository.findByCourseCode(courseCode)
        return [self.toDto(subject) for subject in subjects]

    def getSubject(self, subjectId: int) -> SubjectDTO:
        return self.toDto(self.findSubject(subjectId))

    def createSubject(self, request: SubjectDTO) -> SubjectDTO:
        self.validateRequest(request)
        subject = Subject()
        subject.subjectName = Helpers.trimToNull(request.subjectName)  # type: ignore[assignment]
        subject.subjectCode = Helpers.trimToNull(request.subjectCode)  # type: ignore[assignment]
        subject.courseCode = Helpers.trimToNull(request.courseCode)  # type: ignore[assignment]
        subject.subjectDescription = Helpers.trimToNull(request.subjectDescription)
        return self.toDto(self.subjectRepository.save(subject))

    def updateSubject(self, subjectId: int, request: SubjectDTO) -> SubjectDTO:
        subject = self.findSubject(subjectId)
        self.validateRequest(request)
        subject.subjectName = Helpers.trimToNull(request.subjectName)  # type: ignore[assignment]
        subject.subjectCode = Helpers.trimToNull(request.subjectCode)  # type: ignore[assignment]
        subject.courseCode = Helpers.trimToNull(request.courseCode)  # type: ignore[assignment]
        subject.subjectDescription = Helpers.trimToNull(request.subjectDescription)
        return self.toDto(self.subjectRepository.save(subject))

    def deleteSubject(self, subjectId: int) -> None:
        self.subjectRepository.delete(self.findSubject(subjectId))

    def validateRequest(self, request: SubjectDTO) -> None:
        Validators.requireText(request.subjectName, "subjectName")
        Validators.requireText(request.subjectCode, "subjectCode")
        Validators.requireText(request.courseCode, "courseCode")
        if not self.courseRepository.existsById(request.courseCode.strip() if request.courseCode else None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    def findSubject(self, subjectId: int | None) -> Subject:
        subject = self.subjectRepository.findById(subjectId)
        if subject is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject

    def toDto(self, subject: Subject) -> SubjectDTO:
        return SubjectDTO(
            subjectId=subject.subjectId,
            subjectName=subject.subjectName,
            subjectCode=subject.subjectCode,
            courseCode=subject.courseCode,
            subjectDescription=subject.subjectDescription,
        )
