from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingParticipantDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    userId: int | None = None
    username: str | None = None
    displayName: str | None = None
    role: str | None = None
    invited: bool = False
    joinedAt: datetime | None = None
    leftAt: datetime | None = None
