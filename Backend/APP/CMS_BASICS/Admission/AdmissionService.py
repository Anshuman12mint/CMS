from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Admission.Admission import Admission
from APP.CMS_BASICS.Admission.AdmissionDTO import AdmissionDTO
from APP.CMS_BASICS.Admission.AdmissionRepository import AdmissionRepository
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class AdmissionService:
    def __init__(
        self,
        session: Session,
        admissionRepository: AdmissionRepository,
        studentRepository: StudentRepository,
        courseRepository: CourseRepository,
    ) -> None:
        self.session = session
        self.admissionRepository = admissionRepository
        self.studentRepository = studentRepository
        self.courseRepository = courseRepository

    def getAdmissions(self) -> list[AdmissionDTO]:
        return [self.toDto(admission) for admission in self.admissionRepository.findAdmissions()]

    def getAdmission(self, studentId: int) -> AdmissionDTO:
        admission = self.admissionRepository.findAdmission(studentId)
        if admission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission not found")
        return self.toDto(admission)

    def countAdmissions(self) -> int:
        return self.admissionRepository.countAdmissions()

    def createAdmission(self, request: AdmissionDTO) -> AdmissionDTO:
        student = Student()
        self.apply(student, request)
        return self.toDto(self.toAdmission(self.admissionRepository.save(student)))

    def updateAdmission(self, studentId: int, request: AdmissionDTO) -> AdmissionDTO:
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission not found")
        self.apply(student, request)
        return self.toDto(self.toAdmission(self.admissionRepository.save(student)))

    def deleteAdmission(self, studentId: int) -> None:
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission not found")
        self.admissionRepository.delete(student)

    def apply(self, student: Student, request: AdmissionDTO) -> None:
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

    def toDto(self, admission: Admission) -> AdmissionDTO:
        return AdmissionDTO(
            studentId=admission.studentId,
            firstName=admission.firstName,
            lastName=admission.lastName,
            dob=admission.dob,
            gender=admission.gender,
            phoneNumber=admission.phoneNumber,
            email=admission.email,
            courseCode=admission.courseCode,
            admissionDate=admission.admissionDate,
            address=admission.address,
            guardianName=admission.guardianName,
            guardianContact=admission.guardianContact,
            bloodGroup=admission.bloodGroup,
            createdAt=admission.createdAt,
        )

    def toAdmission(self, student: Student) -> Admission:
        return Admission(
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
