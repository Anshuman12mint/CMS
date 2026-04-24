from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SubjectDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subjectId: int | None = None
    subjectName: str | None = None
    subjectCode: str | None = None
    courseCode: str | None = None
    subjectDescription: str | None = None
