from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Admission.AdmissionRepository import AdmissionRepository
from APP.CMS_BASICS.Admission.AdmissionService import AdmissionService
from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.dashbordbyusers.DashboardService import DashboardService
from APP.CMS_BASICS.dashbordbyusers.DashboardSummaryDTO import DashboardSummaryDTO
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository
from APP.CMS_BASICS.Staff.StaffRepository import StaffRepository
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(getCurrentUser)])


def getDashboardService(session: Session = Depends(getDbSession)) -> DashboardService:
    studentRepository = StudentRepository(session)
    admissionService = AdmissionService(
        session,
        AdmissionRepository(studentRepository),
        studentRepository,
        CourseRepository(session),
    )
    return DashboardService(
        session,
        studentRepository,
        TeacherRepository(session),
        StaffRepository(session),
        CourseRepository(session),
        SubjectRepository(session),
        UserRepository(session),
        AttendanceRepository(session),
        FeeRepository(session),
        StudentMarkRepository(session),
        admissionService,
    )


@router.get("", response_model=DashboardSummaryDTO)
def getSummary(dashboardService: DashboardService = Depends(getDashboardService)) -> DashboardSummaryDTO:
    return dashboardService.getSummary()
