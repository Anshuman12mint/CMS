from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Teacher.Teacher import Teacher


class TeacherRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, teacherId: int | None) -> Teacher | None:
        return None if teacherId is None else self.session.get(Teacher, teacherId)

    def findByEmailIgnoreCase(self, email: str | None) -> Teacher | None:
        if email is None:
            return None
        return self.session.scalar(select(Teacher).where(func.lower(Teacher.email) == email.strip().lower()))

    def findAll(self) -> list[Teacher]:
        return list(self.session.scalars(select(Teacher)))

    def save(self, teacher: Teacher) -> Teacher:
        self.session.add(teacher)
        self.session.flush()
        self.session.refresh(teacher)
        return teacher

    def delete(self, teacher: Teacher) -> None:
        self.session.delete(teacher)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Teacher)) or 0)
