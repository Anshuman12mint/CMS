from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StaffDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staffId: int | None = None
    firstName: str | None = None
    lastName: str | None = None
    dob: date | None = None
    gender: str | None = None
    phoneNumber: str | None = None
    email: str | None = None
    hireDate: date | None = None
    role: str | None = None
    department: str | None = None
    address: str | None = None
    salary: Decimal | None = None
    createdAt: datetime | None = None
