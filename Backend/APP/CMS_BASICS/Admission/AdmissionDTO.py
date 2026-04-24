from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AdmissionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    studentId: int | None = None
    firstName: str | None = None
    lastName: str | None = None
    dob: date | None = None
    gender: str | None = None
    phoneNumber: str | None = None
    email: str | None = None
    courseCode: str | None = None
    admissionDate: date | None = None
    address: str | None = None
    guardianName: str | None = None
    guardianContact: str | None = None
    bloodGroup: str | None = None
    createdAt: datetime | None = None
