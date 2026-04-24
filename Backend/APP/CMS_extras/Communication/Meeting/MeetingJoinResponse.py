from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MeetingJoinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meetingId: int | None = None
    provider: str | None = None
    meetingCode: str | None = None
    roomName: str | None = None
    joinUrl: str | None = None
    displayName: str | None = None
    role: str | None = None
