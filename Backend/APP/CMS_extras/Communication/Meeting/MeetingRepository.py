from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_extras.Communication.Meeting.Meeting import Meeting


class MeetingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, meetingId: int | None) -> Meeting | None:
        return None if meetingId is None else self.session.get(Meeting, meetingId)

    def findAllByOrderByScheduledStartAtDescCreatedAtDesc(self) -> list[Meeting]:
        return list(self.session.scalars(
            select(Meeting).order_by(Meeting.scheduledStartAt.desc(), Meeting.createdAt.desc())
        ))

    def existsByMeetingCode(self, meetingCode: str) -> bool:
        return self.session.scalar(select(func.count()).select_from(Meeting).where(Meeting.meetingCode == meetingCode)) > 0

    def existsByRoomName(self, roomName: str) -> bool:
        return self.session.scalar(select(func.count()).select_from(Meeting).where(Meeting.roomName == roomName)) > 0

    def save(self, meeting: Meeting) -> Meeting:
        self.session.add(meeting)
        self.session.flush()
        self.session.refresh(meeting)
        return meeting

    def delete(self, meeting: Meeting) -> None:
        self.session.delete(meeting)
        self.session.flush()
