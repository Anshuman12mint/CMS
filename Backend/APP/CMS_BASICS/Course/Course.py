from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from APP.Utils.Database.DatabaseConfig import Base


class Course(Base):
    __module__ = "APP.CMS_BASICS.Course.models"
    __tablename__ = "course"

    courseCode: Mapped[str] = mapped_column("course_code", String(10), primary_key=True)
    courseName: Mapped[str] = mapped_column("course_name", String(100), nullable=False)
    courseDescription: Mapped[str | None] = mapped_column("course_description", Text, nullable=True)
