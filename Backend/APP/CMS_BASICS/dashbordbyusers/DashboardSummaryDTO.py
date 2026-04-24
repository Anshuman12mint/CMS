from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from APP.CMS_BASICS.Admission.AdmissionDTO import AdmissionDTO


class DashboardSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    totalStudents: int = 0
    totalTeachers: int = 0
    totalStaff: int = 0
    totalCourses: int = 0
    totalSubjects: int = 0
    totalUsers: int = 0
    totalAdmissions: int = 0
    totalAttendanceRecords: int = 0
    totalMarksRecorded: int = 0
    pendingFeeCount: int = 0
    pendingFeeAmount: Decimal = Decimal("0")
    recentAdmissions: list[AdmissionDTO] = Field(default_factory=list)
