from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, ConfigDict


class AttendanceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attendanceId: int | None = None
    studentId: int | None = None
    date: date_type | None = None
    status: str | None = None
