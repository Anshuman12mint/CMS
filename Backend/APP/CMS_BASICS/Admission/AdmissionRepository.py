from __future__ import annotations

from APP.CMS_BASICS.Admission.Admission import Admission
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository


class AdmissionRepository:
    def __init__(self, studentRepository: StudentRepository) -> None:
        self.studentRepository = studentRepository

    def findAdmissions(self) -> list[Admission]:
        return [self.toAdmission(student) for student in self.studentRepository.findAllByOrderByAdmissionDateDesc()]

    def findAdmission(self, studentId: int) -> Admission | None:
        student = self.studentRepository.findById(studentId)
        return None if student is None else self.toAdmission(student)

    def countAdmissions(self) -> int:
        return self.studentRepository.count()

    def save(self, student: Student) -> Student:
        return self.studentRepository.save(student)

    def delete(self, student: Student) -> None:
        self.studentRepository.delete(student)

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
