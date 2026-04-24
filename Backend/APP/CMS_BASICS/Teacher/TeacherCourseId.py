from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TeacherCourseId:
    teacherId: int | None = None
    courseCode: str | None = None
