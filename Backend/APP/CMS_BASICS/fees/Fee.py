from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from APP.Utils.Database.DatabaseConfig import Base


class Fee(Base):
    __tablename__ = "fees"

    feeId: Mapped[int] = mapped_column("fee_id", Integer, primary_key=True, autoincrement=True)
    studentId: Mapped[int | None] = mapped_column("student_id", ForeignKey("student.student_id"), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column("amount", Numeric(10, 2), nullable=True)
    status: Mapped[str | None] = mapped_column("status", String(20), nullable=True)
    dueDate: Mapped[date | None] = mapped_column("due_date", Date, nullable=True)

    student = relationship("Student")
