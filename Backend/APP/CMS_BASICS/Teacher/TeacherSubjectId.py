from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TeacherSubjectId:
    teacherId: int | None = None
    subjectId: int | None = None
