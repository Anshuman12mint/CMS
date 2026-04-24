from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Attendance.Attendance import Attendance


class AttendanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, attendanceId: int | None) -> Attendance | None:
        return None if attendanceId is None else self.session.get(Attendance, attendanceId)

    def findByStudentStudentIdOrderByDateDesc(self, studentId: int) -> list[Attendance]:
        return list(self.session.scalars(
            select(Attendance).where(Attendance.studentId == studentId).order_by(Attendance.date.desc())
        ))

    def findAllByOrderByDateDesc(self) -> list[Attendance]:
        return list(self.session.scalars(select(Attendance).order_by(Attendance.date.desc())))

    def save(self, attendance: Attendance) -> Attendance:
        self.session.add(attendance)
        self.session.flush()
        self.session.refresh(attendance)
        return attendance

    def saveAll(self, attendanceRows: list[Attendance]) -> list[Attendance]:
        self.session.add_all(attendanceRows)
        self.session.flush()
        return attendanceRows

    def delete(self, attendance: Attendance) -> None:
        self.session.delete(attendance)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Attendance)) or 0)

    def countByStatusIgnoreCase(self, status: str) -> int:
        return int(
            self.session.scalar(
                select(func.count()).select_from(Attendance).where(func.lower(Attendance.status) == status.lower())
            )
            or 0
        )
