from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Marks.StudentMark import StudentMark


class StudentMarkRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, markId: int | None) -> StudentMark | None:
        return None if markId is None else self.session.get(StudentMark, markId)

    def findByStudentStudentIdOrderByExamDateDesc(self, studentId: int) -> list[StudentMark]:
        return list(self.session.scalars(
            select(StudentMark).where(StudentMark.studentId == studentId).order_by(StudentMark.examDate.desc())
        ))

    def findAllByOrderByExamDateDesc(self) -> list[StudentMark]:
        return list(self.session.scalars(select(StudentMark).order_by(StudentMark.examDate.desc())))

    def save(self, mark: StudentMark) -> StudentMark:
        self.session.add(mark)
        self.session.flush()
        self.session.refresh(mark)
        return mark

    def saveAll(self, marks: list[StudentMark]) -> list[StudentMark]:
        self.session.add_all(marks)
        self.session.flush()
        return marks

    def delete(self, mark: StudentMark) -> None:
        self.session.delete(mark)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(StudentMark)) or 0)
