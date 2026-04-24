from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Teacher.TeacherCourse import TeacherCourse


class TeacherCourseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findByTeacherTeacherId(self, teacherId: int) -> list[TeacherCourse]:
        return list(self.session.scalars(select(TeacherCourse).where(TeacherCourse.teacherId == teacherId)))

    def save(self, assignment: TeacherCourse) -> TeacherCourse:
        self.session.add(assignment)
        self.session.flush()
        return assignment

    def saveAll(self, assignments: list[TeacherCourse]) -> list[TeacherCourse]:
        self.session.add_all(assignments)
        self.session.flush()
        return assignments

    def deleteByTeacherTeacherId(self, teacherId: int) -> None:
        self.session.execute(delete(TeacherCourse).where(TeacherCourse.teacherId == teacherId))
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(TeacherCourse)) or 0)
