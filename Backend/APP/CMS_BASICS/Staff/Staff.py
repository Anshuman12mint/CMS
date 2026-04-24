from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from APP.Utils.Database.DatabaseConfig import Base


class Staff(Base):
    __module__ = "APP.CMS_BASICS.Staff.models"
    __tablename__ = "staff"

    staffId: Mapped[int] = mapped_column("staff_id", Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column("first_name", String(50), nullable=False)
    lastName: Mapped[str] = mapped_column("last_name", String(50), nullable=False)
    dob: Mapped[date] = mapped_column("dob", Date, nullable=False)
    gender: Mapped[str] = mapped_column("gender", String(20), nullable=False)
    phoneNumber: Mapped[str] = mapped_column("phone_number", String(15), unique=True, nullable=False)
    email: Mapped[str] = mapped_column("email", String(100), unique=True, nullable=False)
    hireDate: Mapped[date] = mapped_column("hire_date", Date, nullable=False)
    role: Mapped[str] = mapped_column("role", String(50), nullable=False)
    department: Mapped[str | None] = mapped_column("department", String(100), nullable=True)
    address: Mapped[str | None] = mapped_column("address", Text, nullable=True)
    salary: Mapped[Decimal | None] = mapped_column("salary", Numeric(10, 2), nullable=True)
    createdAt: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
