from __future__ import annotations

from APP.Utils.Config.AppConfig import getSettings
from APP.CMS_extras.Communication.Meeting.Meeting import Meeting
from APP.CMS_extras.Communication.Meeting.MeetingJoinResponse import MeetingJoinResponse
from APP.CMS_BASICS.Login_resister.User import User
from APP.Utils.Helpers import Helpers


class MeetingProviderService:
    def __init__(self) -> None:
        settings = getSettings()
        self._provider = self.normalizeProvider(settings.meetingsProvider)
        self.jitsiBaseUrl = self.normalizeBaseUrl(settings.meetingsJitsiBaseUrl)

    def provider(self) -> str:
        return self._provider

    def generateRoomName(self, meetingCode: str) -> str:
        sanitized = "".join(ch.lower() if ch.isalnum() else "-" for ch in meetingCode.lower())
        return "cms-" + sanitized.strip("-")

    def buildJoinUrl(self, roomName: str) -> str:
        if self._provider != "Jitsi":
            return roomName
        return f"{self.jitsiBaseUrl}/{roomName}"

    def toJoinResponse(self, meeting: Meeting, user: User, role: str | None, displayName: str | None) -> MeetingJoinResponse:
        name = Helpers.trimToNull(displayName)
        return MeetingJoinResponse(
            meetingId=meeting.meetingId,
            provider=meeting.provider,
            meetingCode=meeting.meetingCode,
            roomName=meeting.roomName,
            joinUrl=self.buildJoinUrl(meeting.roomName),
            displayName=user.username if name is None else name.strip(),
            role=role,
        )

    def normalizeProvider(self, value: str | None) -> str:
        normalized = Helpers.trimToNull(value)
        if normalized is None or normalized.lower() == "jitsi":
            return "Jitsi"
        return normalized

    def normalizeBaseUrl(self, value: str | None) -> str:
        normalized = Helpers.trimToNull(value)
        if normalized is None:
            return "https://meet.jit.si"
        return normalized[:-1] if normalized.endswith("/") else normalized
