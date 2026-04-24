from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from APP.Utils.Database.DatabaseConfig import Base
from APP.CMS_BASICS.Teacher.TeacherSubjectId import TeacherSubjectId


class TeacherSubject(Base):
    __tablename__ = "teacher_subject"

    teacherId: Mapped[int] = mapped_column("teacher_id", ForeignKey("teacher.teacher_id"), primary_key=True)
    subjectId: Mapped[int] = mapped_column("subject_id", ForeignKey("subject.subject_id"), primary_key=True)

    teacher = relationship("Teacher")
    subject = relationship("Subject")

    @property
    def id(self) -> TeacherSubjectId:
        return TeacherSubjectId(self.teacherId, self.subjectId)

    @id.setter
    def id(self, value: TeacherSubjectId) -> None:
        self.teacherId = value.teacherId  # type: ignore[assignment]
        self.subjectId = value.subjectId  # type: ignore[assignment]
