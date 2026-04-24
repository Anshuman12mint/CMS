from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    userId: int | None = None
    username: str | None = None
    email: str | None = None
    role: str | None = None
    studentId: int | None = None
    createdAt: datetime | None = None
