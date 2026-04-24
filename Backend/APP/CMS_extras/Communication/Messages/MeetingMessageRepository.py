from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from APP.CMS_extras.Communication.Messages.MeetingMessage import MeetingMessage


class MeetingMessageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findByMeetingMeetingIdOrderByCreatedAtAsc(self, meetingId: int) -> list[MeetingMessage]:
        return list(self.session.scalars(
            select(MeetingMessage).where(MeetingMessage.meetingId == meetingId).order_by(MeetingMessage.createdAt.asc())
        ))

    def save(self, message: MeetingMessage) -> MeetingMessage:
        self.session.add(message)
        self.session.flush()
        self.session.refresh(message)
        return message
