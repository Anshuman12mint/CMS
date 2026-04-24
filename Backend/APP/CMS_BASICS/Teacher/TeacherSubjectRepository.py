from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Teacher.TeacherSubject import TeacherSubject


class TeacherSubjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findByTeacherTeacherId(self, teacherId: int) -> list[TeacherSubject]:
        return list(self.session.scalars(select(TeacherSubject).where(TeacherSubject.teacherId == teacherId)))

    def save(self, assignment: TeacherSubject) -> TeacherSubject:
        self.session.add(assignment)
        self.session.flush()
        return assignment

    def saveAll(self, assignments: list[TeacherSubject]) -> list[TeacherSubject]:
        self.session.add_all(assignments)
        self.session.flush()
        return assignments

    def deleteByTeacherTeacherId(self, teacherId: int) -> None:
        self.session.execute(delete(TeacherSubject).where(TeacherSubject.teacherId == teacherId))
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(TeacherSubject)) or 0)
