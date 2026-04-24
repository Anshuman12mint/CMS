from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from APP.Utils.Database.DatabaseConfig import Base


class Attendance(Base):
    __module__ = "APP.CMS_BASICS.Attendance.models"
    __tablename__ = "attendance"

    attendanceId: Mapped[int] = mapped_column("attendance_id", Integer, primary_key=True, autoincrement=True)
    studentId: Mapped[int | None] = mapped_column("student_id", ForeignKey("student.student_id"), nullable=True)
    date: Mapped[date_type | None] = mapped_column("date", Date, nullable=True)
    status: Mapped[str | None] = mapped_column("status", String(20), nullable=True)

    student = relationship("Student")
