from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FeeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feeId: int | None = None
    studentId: int | None = None
    amount: Decimal | None = None
    status: str | None = None
    dueDate: date | None = None
