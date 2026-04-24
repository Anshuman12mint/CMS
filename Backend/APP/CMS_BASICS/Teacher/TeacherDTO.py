from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TeacherDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    teacherId: int | None = None
    firstName: str | None = None
    lastName: str | None = None
    dob: date | None = None
    gender: str | None = None
    phoneNumber: str | None = None
    email: str | None = None
    hireDate: date | None = None
    department: str | None = None
    address: str | None = None
    qualification: str | None = None
    salary: Decimal | None = None
    createdAt: datetime | None = None
    courseCodes: list[str] = Field(default_factory=list)
    subjectIds: list[int] = Field(default_factory=list)
