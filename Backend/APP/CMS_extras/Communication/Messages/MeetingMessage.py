from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from APP.Utils.Database.DatabaseConfig import Base


class MeetingMessage(Base):
    __tablename__ = "meeting_message"

    messageId: Mapped[int] = mapped_column("message_id", Integer, primary_key=True, autoincrement=True)
    meetingId: Mapped[int] = mapped_column("meeting_id", ForeignKey("meeting_room.meeting_id"), nullable=False)
    userId: Mapped[int] = mapped_column("user_id", ForeignKey("users.user_id"), nullable=False)
    messageText: Mapped[str] = mapped_column("message_text", Text, nullable=False)
    createdAt: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting")
    user = relationship("User")
