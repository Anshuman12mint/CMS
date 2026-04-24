from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from APP.CMS_extras.Communication.Meeting.MeetingParticipant import MeetingParticipant


class MeetingParticipantRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findByMeetingMeetingIdOrderByCreatedAtAsc(self, meetingId: int) -> list[MeetingParticipant]:
        return list(self.session.scalars(
            select(MeetingParticipant).where(MeetingParticipant.meetingId == meetingId).order_by(MeetingParticipant.createdAt.asc())
        ))

    def findByMeetingMeetingIdAndUserUserId(self, meetingId: int, userId: int) -> MeetingParticipant | None:
        return self.session.scalar(
            select(MeetingParticipant).where(
                MeetingParticipant.meetingId == meetingId,
                MeetingParticipant.userId == userId,
            )
        )

    def existsByMeetingMeetingIdAndUserUserId(self, meetingId: int, userId: int) -> bool:
        return self.session.scalar(
            select(func.count()).select_from(MeetingParticipant).where(
                MeetingParticipant.meetingId == meetingId,
                MeetingParticipant.userId == userId,
            )
        ) > 0

    def save(self, participant: MeetingParticipant) -> MeetingParticipant:
        self.session.add(participant)
        self.session.flush()
        self.session.refresh(participant)
        return participant

    def deleteByMeetingMeetingIdAndRoleAndInvited(self, meetingId: int, role: str, invited: bool) -> None:
        self.session.execute(
            delete(MeetingParticipant).where(
                MeetingParticipant.meetingId == meetingId,
                MeetingParticipant.role == role,
                MeetingParticipant.invited == invited,
            )
        )
        self.session.flush()

    def deleteByMeetingMeetingId(self, meetingId: int) -> None:
        self.session.execute(delete(MeetingParticipant).where(MeetingParticipant.meetingId == meetingId))
        self.session.flush()
