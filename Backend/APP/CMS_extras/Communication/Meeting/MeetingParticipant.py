from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from APP.Utils.Database.DatabaseConfig import Base


class MeetingParticipant(Base):
    __tablename__ = "meeting_participant"
    __table_args__ = (
        UniqueConstraint("meeting_id", "user_id", name="uk_meeting_participant_meeting_user"),
    )

    meetingParticipantId: Mapped[int] = mapped_column("meeting_participant_id", Integer, primary_key=True, autoincrement=True)
    meetingId: Mapped[int] = mapped_column("meeting_id", ForeignKey("meeting_room.meeting_id"), nullable=False)
    userId: Mapped[int] = mapped_column("user_id", ForeignKey("users.user_id"), nullable=False)
    role: Mapped[str] = mapped_column("role", String(20), nullable=False)
    invited: Mapped[bool] = mapped_column("invited", Boolean, nullable=False, default=False)
    joinedAt: Mapped[datetime | None] = mapped_column("joined_at", DateTime(timezone=True), nullable=True)
    leftAt: Mapped[datetime | None] = mapped_column("left_at", DateTime(timezone=True), nullable=True)
    createdAt: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting")
    user = relationship("User")
