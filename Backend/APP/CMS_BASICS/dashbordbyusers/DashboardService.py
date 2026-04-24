from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Admission.AdmissionService import AdmissionService
from APP.CMS_BASICS.dashbordbyusers.DashboardSummaryDTO import DashboardSummaryDTO
from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository
from APP.CMS_BASICS.Staff.StaffRepository import StaffRepository
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository


class DashboardService:
    def __init__(
        self,
        session: Session,
        studentRepository: StudentRepository,
        teacherRepository: TeacherRepository,
        staffRepository: StaffRepository,
        courseRepository: CourseRepository,
        subjectRepository: SubjectRepository,
        userRepository: UserRepository,
        attendanceRepository: AttendanceRepository,
        feeRepository: FeeRepository,
        studentMarkRepository: StudentMarkRepository,
        admissionService: AdmissionService,
    ) -> None:
        self.session = session
        self.studentRepository = studentRepository
        self.teacherRepository = teacherRepository
        self.staffRepository = staffRepository
        self.courseRepository = courseRepository
        self.subjectRepository = subjectRepository
        self.userRepository = userRepository
        self.attendanceRepository = attendanceRepository
        self.feeRepository = feeRepository
        self.studentMarkRepository = studentMarkRepository
        self.admissionService = admissionService

    def getSummary(self) -> DashboardSummaryDTO:
        recentAdmissions = self.admissionService.getAdmissions()[:5]
        return DashboardSummaryDTO(
            totalStudents=self.studentRepository.count(),
            totalTeachers=self.teacherRepository.count(),
            totalStaff=self.staffRepository.count(),
            totalCourses=self.courseRepository.count(),
            totalSubjects=self.subjectRepository.count(),
            totalUsers=self.userRepository.count(),
            totalAdmissions=self.admissionService.countAdmissions(),
            totalAttendanceRecords=self.attendanceRepository.count(),
            totalMarksRecorded=self.studentMarkRepository.count(),
            pendingFeeCount=self.feeRepository.countByStatusIgnoreCase("Pending"),
            pendingFeeAmount=self.feeRepository.sumPendingAmount() or Decimal("0"),
            recentAdmissions=recentAdmissions,
        )
