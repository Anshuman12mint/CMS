from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from APP.Utils.Database.DatabaseConfig import Base


class Meeting(Base):
    __module__ = "APP.CMS_extras.Communication.Meeting.models"
    __tablename__ = "meeting_room"

    meetingId: Mapped[int] = mapped_column("meeting_id", Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column("title", String(150), nullable=False)
    description: Mapped[str | None] = mapped_column("description", Text, nullable=True)
    provider: Mapped[str] = mapped_column("provider", String(30), nullable=False)
    meetingCode: Mapped[str] = mapped_column("meeting_code", String(20), unique=True, nullable=False)
    roomName: Mapped[str] = mapped_column("room_name", String(120), unique=True, nullable=False)
    status: Mapped[str] = mapped_column("status", String(20), nullable=False)
    audienceType: Mapped[str] = mapped_column("audience_type", String(20), nullable=False)
    courseCode: Mapped[str | None] = mapped_column("course_code", String(10), nullable=True)
    scheduledStartAt: Mapped[datetime] = mapped_column("scheduled_start_at", DateTime(timezone=True), nullable=False)
    scheduledEndAt: Mapped[datetime | None] = mapped_column("scheduled_end_at", DateTime(timezone=True), nullable=True)
    startedAt: Mapped[datetime | None] = mapped_column("started_at", DateTime(timezone=True), nullable=True)
    endedAt: Mapped[datetime | None] = mapped_column("ended_at", DateTime(timezone=True), nullable=True)
    createdByUserId: Mapped[int] = mapped_column("created_by_user_id", ForeignKey("users.user_id"), nullable=False)
    createdAt: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    createdBy = relationship("User")
