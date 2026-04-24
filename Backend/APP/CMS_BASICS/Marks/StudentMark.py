from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from APP.Utils.Database.DatabaseConfig import Base


class StudentMark(Base):
    __tablename__ = "student_marks"

    markId: Mapped[int] = mapped_column("mark_id", Integer, primary_key=True, autoincrement=True)
    studentId: Mapped[int] = mapped_column("student_id", ForeignKey("student.student_id"), nullable=False)
    subjectId: Mapped[int] = mapped_column("subject_id", ForeignKey("subject.subject_id"), nullable=False)
    semester: Mapped[int] = mapped_column("semester", Integer, nullable=False)
    examType: Mapped[str] = mapped_column("exam_type", String(20), nullable=False)
    marksObtained: Mapped[Decimal] = mapped_column("marks_obtained", Numeric(5, 2), nullable=False)
    maxMarks: Mapped[Decimal] = mapped_column("max_marks", Numeric(5, 2), nullable=False)
    grade: Mapped[str | None] = mapped_column("grade", String(2), nullable=True)
    examDate: Mapped[date] = mapped_column("exam_date", Date, nullable=False)
    createdAt: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    subject = relationship("Subject")
