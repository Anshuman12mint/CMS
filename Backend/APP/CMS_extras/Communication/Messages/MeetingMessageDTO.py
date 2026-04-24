from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingMessageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    messageId: int | None = None
    meetingId: int | None = None
    userId: int | None = None
    username: str | None = None
    displayName: str | None = None
    messageText: str | None = None
    createdAt: datetime | None = None
