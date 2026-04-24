from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Subject.Subject import Subject


class SubjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, subjectId: int | None) -> Subject | None:
        return None if subjectId is None else self.session.get(Subject, subjectId)

    def findByCourseCode(self, courseCode: str) -> list[Subject]:
        return list(self.session.scalars(select(Subject).where(Subject.courseCode == courseCode)))

    def findAllBySubjectIdIn(self, subjectIds: list[int]) -> list[Subject]:
        if not subjectIds:
            return []
        return list(self.session.scalars(select(Subject).where(Subject.subjectId.in_(subjectIds))))

    def findAll(self) -> list[Subject]:
        return list(self.session.scalars(select(Subject)))

    def save(self, subject: Subject) -> Subject:
        self.session.add(subject)
        self.session.flush()
        self.session.refresh(subject)
        return subject

    def delete(self, subject: Subject) -> None:
        self.session.delete(subject)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Subject)) or 0)
