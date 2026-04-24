from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from APP.CMS_BASICS.Course.CourseDTO import CourseDTO
from APP.CMS_BASICS.Subject.SubjectDTO import SubjectDTO
from APP.CMS_BASICS.Teacher.TeacherDTO import TeacherDTO


class TeacherReportDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    teacher: TeacherDTO | None = None
    courses: list[CourseDTO] = Field(default_factory=list)
    subjects: list[SubjectDTO] = Field(default_factory=list)
