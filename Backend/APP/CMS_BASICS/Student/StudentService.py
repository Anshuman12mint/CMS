from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentDTO import StudentDTO
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class StudentService:
    def __init__(self, session: Session, studentRepository: StudentRepository, courseRepository: CourseRepository) -> None:
        self.session = session
        self.studentRepository = studentRepository
        self.courseRepository = courseRepository

    def getAllStudents(self, courseCode: str | None) -> list[StudentDTO]:
        students = (
            self.studentRepository.findByCourseCodeOrderByAdmissionDateDesc(courseCode.strip())
            if Validators.hasText(courseCode)
            else self.studentRepository.findAllByOrderByAdmissionDateDesc()
        )
        return [self.toDto(student) for student in students]

    def getStudent(self, studentId: int) -> StudentDTO:
        return self.toDto(self.findStudent(studentId))

    def createStudent(self, request: StudentDTO) -> StudentDTO:
        student = Student()
        self.apply(student, request)
        return self.toDto(self.studentRepository.save(student))

    def updateStudent(self, studentId: int, request: StudentDTO) -> StudentDTO:
        student = self.findStudent(studentId)
        self.apply(student, request)
        return self.toDto(self.studentRepository.save(student))

    def deleteStudent(self, studentId: int) -> None:
        self.studentRepository.delete(self.findStudent(studentId))

    def findStudent(self, studentId: int | None) -> Student:
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def apply(self, student: Student, request: StudentDTO) -> None:
        Validators.requireText(request.firstName, "firstName")
        Validators.requireText(request.lastName, "lastName")
        Validators.require(request.dob is not None, "dob is required")
        Validators.require(request.admissionDate is not None, "admissionDate is required")
        Validators.requireText(request.phoneNumber, "phoneNumber")
        Validators.requireText(request.email, "email")
        Validators.requireText(request.courseCode, "courseCode")

        courseCode = Helpers.trimToNull(request.courseCode)
        if not self.courseRepository.existsById(courseCode):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        student.firstName = Helpers.trimToNull(request.firstName)  # type: ignore[assignment]
        student.lastName = Helpers.trimToNull(request.lastName)  # type: ignore[assignment]
        student.dob = request.dob  # type: ignore[assignment]
        student.gender = Validators.normalizeRequiredChoice(request.gender, Validators.GENDERS, "gender")
        student.phoneNumber = Helpers.trimToNull(request.phoneNumber)  # type: ignore[assignment]
        student.email = Helpers.trimToNull(request.email)  # type: ignore[assignment]
        student.courseCode = courseCode  # type: ignore[assignment]
        student.admissionDate = request.admissionDate  # type: ignore[assignment]
        student.address = Helpers.trimToNull(request.address)
        student.guardianName = Helpers.trimToNull(request.guardianName)
        student.guardianContact = Helpers.trimToNull(request.guardianContact)
        student.bloodGroup = Validators.normalizeOptionalChoice(request.bloodGroup, Validators.BLOOD_GROUPS, "bloodGroup")

    def toDto(self, student: Student) -> StudentDTO:
        return StudentDTO(
            studentId=student.studentId,
            firstName=student.firstName,
            lastName=student.lastName,
            dob=student.dob,
            gender=student.gender,
            phoneNumber=student.phoneNumber,
            email=student.email,
            courseCode=student.courseCode,
            admissionDate=student.admissionDate,
            address=student.address,
            guardianName=student.guardianName,
            guardianContact=student.guardianContact,
            bloodGroup=student.bloodGroup,
            createdAt=student.createdAt,
        )
