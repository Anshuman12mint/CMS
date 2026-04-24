from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from APP.CMS_BASICS.Attendance.AttendanceDTO import AttendanceDTO
from APP.CMS_BASICS.fees.FeeDTO import FeeDTO
from APP.CMS_BASICS.Marks.StudentMarkDTO import StudentMarkDTO
from APP.CMS_BASICS.Student.StudentDTO import StudentDTO


class StudentReportDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student: StudentDTO | None = None
    presentDays: int = 0
    absentDays: int = 0
    totalFees: Decimal = Decimal("0")
    paidFees: Decimal = Decimal("0")
    pendingFeesAmount: Decimal = Decimal("0")
    attendance: list[AttendanceDTO] = Field(default_factory=list)
    fees: list[FeeDTO] = Field(default_factory=list)
    marks: list[StudentMarkDTO] = Field(default_factory=list)
