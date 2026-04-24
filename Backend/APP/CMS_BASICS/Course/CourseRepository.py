from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Course.Course import Course


class CourseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, courseCode: str | None) -> Course | None:
        return None if courseCode is None else self.session.get(Course, courseCode)

    def existsById(self, courseCode: str | None) -> bool:
        return self.findById(courseCode) is not None

    def findAll(self) -> list[Course]:
        return list(self.session.scalars(select(Course)))

    def save(self, course: Course) -> Course:
        self.session.add(course)
        self.session.flush()
        self.session.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.session.delete(course)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Course)) or 0)
