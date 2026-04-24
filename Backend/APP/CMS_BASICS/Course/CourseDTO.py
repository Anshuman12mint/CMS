from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CourseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    courseCode: str | None = None
    courseName: str | None = None
    courseDescription: str | None = None
