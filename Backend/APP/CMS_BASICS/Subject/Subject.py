from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from APP.Utils.Database.DatabaseConfig import Base


class Subject(Base):
    __module__ = "APP.CMS_BASICS.Subject.models"
    __tablename__ = "subject"

    subjectId: Mapped[int] = mapped_column("subject_id", Integer, primary_key=True, autoincrement=True)
    subjectName: Mapped[str] = mapped_column("subject_name", String(100), nullable=False)
    subjectCode: Mapped[str] = mapped_column("subject_code", String(10), unique=True, nullable=False)
    courseCode: Mapped[str] = mapped_column("course_code", String(10), nullable=False)
    subjectDescription: Mapped[str | None] = mapped_column("subject_description", Text, nullable=True)
