from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Marks.StudentMark import StudentMark
from APP.CMS_BASICS.Marks.StudentMarkDTO import StudentMarkDTO
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Subject.Subject import Subject
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.Utils.Validators import Validators


class StudentMarkService:
    def __init__(
        self,
        session: Session,
        studentMarkRepository: StudentMarkRepository,
        studentRepository: StudentRepository,
        subjectRepository: SubjectRepository,
    ) -> None:
        self.session = session
        self.studentMarkRepository = studentMarkRepository
        self.studentRepository = studentRepository
        self.subjectRepository = subjectRepository

    def getMarks(self, studentId: int | None) -> list[StudentMarkDTO]:
        rows = (
            self.studentMarkRepository.findAllByOrderByExamDateDesc()
            if studentId is None
            else self.studentMarkRepository.findByStudentStudentIdOrderByExamDateDesc(studentId)
        )
        return [self.toDto(row) for row in rows]

    def getMark(self, markId: int) -> StudentMarkDTO:
        return self.toDto(self.findMark(markId))

    def createMark(self, request: StudentMarkDTO) -> StudentMarkDTO:
        mark = StudentMark()
        self.apply(mark, request)
        return self.toDto(self.studentMarkRepository.save(mark))

    def updateMark(self, markId: int, request: StudentMarkDTO) -> StudentMarkDTO:
        mark = self.findMark(markId)
        self.apply(mark, request)
        return self.toDto(self.studentMarkRepository.save(mark))

    def deleteMark(self, markId: int) -> None:
        self.studentMarkRepository.delete(self.findMark(markId))

    def apply(self, mark: StudentMark, request: StudentMarkDTO) -> None:
        mark.student = self.findStudent(request.studentId)
        mark.studentId = mark.student.studentId  # type: ignore[assignment]
        mark.subject = self.findSubject(request.subjectId)
        mark.subjectId = mark.subject.subjectId  # type: ignore[assignment]
        Validators.require(request.semester is not None, "semester is required")
        Validators.require(request.examDate is not None, "examDate is required")
        Validators.require(request.marksObtained is not None, "marksObtained is required")
        Validators.require(request.maxMarks is not None, "maxMarks is required")
        mark.semester = request.semester
        mark.examType = Validators.normalizeRequiredChoice(request.examType, Validators.EXAM_TYPES, "examType")
        mark.marksObtained = request.marksObtained
        mark.maxMarks = request.maxMarks
        mark.grade = request.grade
        mark.examDate = request.examDate

    def findMark(self, markId: int | None) -> StudentMark:
        mark = self.studentMarkRepository.findById(markId)
        if mark is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mark not found")
        return mark

    def findStudent(self, studentId: int | None) -> Student:
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def findSubject(self, subjectId: int | None) -> Subject:
        subject = self.subjectRepository.findById(subjectId)
        if subject is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        return subject

    def toDto(self, mark: StudentMark) -> StudentMarkDTO:
        return StudentMarkDTO(
            markId=mark.markId,
            studentId=mark.student.studentId if mark.student is not None else mark.studentId,
            subjectId=mark.subject.subjectId if mark.subject is not None else mark.subjectId,
            semester=mark.semester,
            examType=mark.examType,
            marksObtained=mark.marksObtained,
            maxMarks=mark.maxMarks,
            grade=mark.grade,
            examDate=mark.examDate,
        )
