from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from APP.Utils.Database.DatabaseConfig import Base
from APP.CMS_BASICS.Teacher.TeacherCourseId import TeacherCourseId


class TeacherCourse(Base):
    __tablename__ = "teacher_course"

    teacherId: Mapped[int] = mapped_column("teacher_id", ForeignKey("teacher.teacher_id"), primary_key=True)
    courseCode: Mapped[str] = mapped_column("course_code", ForeignKey("course.course_code"), primary_key=True)

    teacher = relationship("Teacher")
    course = relationship("Course")

    @property
    def id(self) -> TeacherCourseId:
        return TeacherCourseId(self.teacherId, self.courseCode)

    @id.setter
    def id(self, value: TeacherCourseId) -> None:
        self.teacherId = value.teacherId  # type: ignore[assignment]
        self.courseCode = value.courseCode  # type: ignore[assignment]
