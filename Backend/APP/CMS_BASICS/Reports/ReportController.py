from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.CMS_BASICS.Attendance.AttendanceService import AttendanceService
from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Course.CourseService import CourseService
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.fees.FeeService import FeeService
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository
from APP.CMS_BASICS.Marks.StudentMarkService import StudentMarkService
from APP.CMS_BASICS.Reports.FeeSummaryDTO import FeeSummaryDTO
from APP.CMS_BASICS.Reports.ReportService import ReportService
from APP.CMS_BASICS.Reports.StudentReportDTO import StudentReportDTO
from APP.CMS_BASICS.Reports.TeacherReportDTO import TeacherReportDTO
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Student.StudentService import StudentService
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Subject.SubjectService import SubjectService
from APP.CMS_BASICS.Teacher.TeacherCourseRepository import TeacherCourseRepository
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Teacher.TeacherService import TeacherService
from APP.CMS_BASICS.Teacher.TeacherSubjectRepository import TeacherSubjectRepository

router = APIRouter(prefix="/api/reports", tags=["reports"], dependencies=[Depends(getCurrentUser)])


def getReportService(session: Session = Depends(getDbSession)) -> ReportService:
    studentRepository = StudentRepository(session)
    subjectRepository = SubjectRepository(session)
    courseRepository = CourseRepository(session)
    return ReportService(
        session,
        StudentService(session, studentRepository, courseRepository),
        TeacherService(
            session,
            TeacherRepository(session),
            courseRepository,
            subjectRepository,
            TeacherCourseRepository(session),
            TeacherSubjectRepository(session),
        ),
        AttendanceService(session, AttendanceRepository(session), studentRepository),
        FeeService(session, FeeRepository(session), studentRepository),
        StudentMarkService(session, StudentMarkRepository(session), studentRepository, subjectRepository),
        CourseService(session, courseRepository),
        SubjectService(session, subjectRepository, courseRepository),
    )


@router.get("/students/{studentId}", response_model=StudentReportDTO)
def getStudentReport(studentId: int, reportService: ReportService = Depends(getReportService)) -> StudentReportDTO:
    return reportService.getStudentReport(studentId)


@router.get("/teachers/{teacherId}", response_model=TeacherReportDTO)
def getTeacherReport(teacherId: int, reportService: ReportService = Depends(getReportService)) -> TeacherReportDTO:
    return reportService.getTeacherReport(teacherId)


@router.get("/fees/summary", response_model=FeeSummaryDTO)
def getFeeSummary(reportService: ReportService = Depends(getReportService)) -> FeeSummaryDTO:
    return reportService.getFeeSummary()
