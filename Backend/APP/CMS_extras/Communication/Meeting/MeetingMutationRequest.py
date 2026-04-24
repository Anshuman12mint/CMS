from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MeetingMutationRequest(BaseModel):
    title: str
    description: str | None = None
    courseCode: str | None = None
    scheduledStartAt: datetime
    scheduledEndAt: datetime | None = None
    participantUserIds: list[int] | None = Field(default=None)
