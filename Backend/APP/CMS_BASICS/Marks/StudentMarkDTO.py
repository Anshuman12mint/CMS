from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StudentMarkDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    markId: int | None = None
    studentId: int | None = None
    subjectId: int | None = None
    semester: int | None = None
    examType: str | None = None
    marksObtained: Decimal | None = None
    maxMarks: Decimal | None = None
    grade: str | None = None
    examDate: date | None = None
