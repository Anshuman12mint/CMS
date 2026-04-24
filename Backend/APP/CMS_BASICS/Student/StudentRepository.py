from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Student.Student import Student


class StudentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, studentId: int | None) -> Student | None:
        return None if studentId is None else self.session.get(Student, studentId)

    def findByEmailIgnoreCase(self, email: str | None) -> Student | None:
        if email is None:
            return None
        return self.session.scalar(select(Student).where(func.lower(Student.email) == email.strip().lower()))

    def existsById(self, studentId: int | None) -> bool:
        if studentId is None:
            return False
        return bool(self.session.scalar(select(func.count()).select_from(Student).where(Student.studentId == studentId)))

    def findByCourseCodeOrderByAdmissionDateDesc(self, courseCode: str) -> list[Student]:
        return list(self.session.scalars(
            select(Student).where(Student.courseCode == courseCode).order_by(Student.admissionDate.desc())
        ))

    def findAllByOrderByAdmissionDateDesc(self) -> list[Student]:
        return list(self.session.scalars(select(Student).order_by(Student.admissionDate.desc())))

    def findAll(self) -> list[Student]:
        return list(self.session.scalars(select(Student)))

    def save(self, student: Student) -> Student:
        self.session.add(student)
        self.session.flush()
        self.session.refresh(student)
        return student

    def delete(self, student: Student) -> None:
        self.session.delete(student)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Student)) or 0)
