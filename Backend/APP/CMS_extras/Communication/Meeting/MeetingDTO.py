from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from APP.CMS_extras.Communication.Meeting.MeetingParticipantDTO import MeetingParticipantDTO


class MeetingDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meetingId: int | None = None
    title: str | None = None
    description: str | None = None
    provider: str | None = None
    meetingCode: str | None = None
    roomName: str | None = None
    joinUrl: str | None = None
    status: str | None = None
    audienceType: str | None = None
    courseCode: str | None = None
    scheduledStartAt: datetime | None = None
    scheduledEndAt: datetime | None = None
    startedAt: datetime | None = None
    endedAt: datetime | None = None
    hostUserId: int | None = None
    hostUsername: str | None = None
    viewerRole: str | None = None
    canManage: bool = False
    canJoin: bool = False
    createdAt: datetime | None = None
    participants: list[MeetingParticipantDTO] = Field(default_factory=list)
