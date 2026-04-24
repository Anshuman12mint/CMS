from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from APP.Utils.Database.DatabaseConfig import Base


class User(Base):
    __tablename__ = "users"

    userId: Mapped[int] = mapped_column("user_id", Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column("username", String(50), unique=True, nullable=False)
    passwordHash: Mapped[str] = mapped_column("password_hash", String(255), nullable=False)
    email: Mapped[str] = mapped_column("email", String(100), unique=True, nullable=False)
    role: Mapped[str] = mapped_column("role", String(20), nullable=False)
    createdAt: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    studentId: Mapped[int | None] = mapped_column("student_id", ForeignKey("student.student_id"), nullable=True)

    student = relationship("Student")
