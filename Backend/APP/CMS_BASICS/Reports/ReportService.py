from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Attendance.AttendanceDTO import AttendanceDTO
from APP.CMS_BASICS.Attendance.AttendanceService import AttendanceService
from APP.CMS_BASICS.Course.CourseDTO import CourseDTO
from APP.CMS_BASICS.Course.CourseService import CourseService
from APP.CMS_BASICS.fees.FeeDTO import FeeDTO
from APP.CMS_BASICS.fees.FeeService import FeeService
from APP.CMS_BASICS.Marks.StudentMarkDTO import StudentMarkDTO
from APP.CMS_BASICS.Marks.StudentMarkService import StudentMarkService
from APP.CMS_BASICS.Reports.FeeSummaryDTO import FeeSummaryDTO
from APP.CMS_BASICS.Reports.StudentReportDTO import StudentReportDTO
from APP.CMS_BASICS.Reports.TeacherReportDTO import TeacherReportDTO
from APP.CMS_BASICS.Student.StudentService import StudentService
from APP.CMS_BASICS.Subject.SubjectDTO import SubjectDTO
from APP.CMS_BASICS.Subject.SubjectService import SubjectService
from APP.CMS_BASICS.Teacher.TeacherService import TeacherService


class ReportService:
    def __init__(
        self,
        session: Session,
        studentService: StudentService,
        teacherService: TeacherService,
        attendanceService: AttendanceService,
        feeService: FeeService,
        studentMarkService: StudentMarkService,
        courseService: CourseService,
        subjectService: SubjectService,
    ) -> None:
        self.session = session
        self.studentService = studentService
        self.teacherService = teacherService
        self.attendanceService = attendanceService
        self.feeService = feeService
        self.studentMarkService = studentMarkService
        self.courseService = courseService
        self.subjectService = subjectService

    def getStudentReport(self, studentId: int) -> StudentReportDTO:
        student = self.studentService.getStudent(studentId)
        attendance = self.attendanceService.getAttendance(studentId)
        fees = self.feeService.getFees(studentId)
        marks = self.studentMarkService.getMarks(studentId)

        presentDays = sum(1 for item in attendance if (item.status or "").lower() == "present")
        absentDays = sum(1 for item in attendance if (item.status or "").lower() == "absent")

        return StudentReportDTO(
            student=student,
            presentDays=presentDays,
            absentDays=absentDays,
            totalFees=self.sumFees(fees, lambda fee: True),
            paidFees=self.sumFees(fees, lambda fee: (fee.status or "").lower() == "paid"),
            pendingFeesAmount=self.sumFees(fees, lambda fee: (fee.status or "").lower() == "pending"),
            attendance=attendance,
            fees=fees,
            marks=marks,
        )

    def getTeacherReport(self, teacherId: int) -> TeacherReportDTO:
        teacher = self.teacherService.getTeacher(teacherId)
        courses: list[CourseDTO] = [self.courseService.getCourse(courseCode) for courseCode in teacher.courseCodes]
        subjects: list[SubjectDTO] = [self.subjectService.getSubject(subjectId) for subjectId in teacher.subjectIds]
        return TeacherReportDTO(teacher=teacher, courses=courses, subjects=subjects)

    def getFeeSummary(self) -> FeeSummaryDTO:
        fees = self.feeService.getFees(None)
        pendingFees = [fee for fee in fees if (fee.status or "").lower() == "pending"]
        return FeeSummaryDTO(
            paidCount=sum(1 for fee in fees if (fee.status or "").lower() == "paid"),
            pendingCount=len(pendingFees),
            paidAmount=self.sumFees(fees, lambda fee: (fee.status or "").lower() == "paid"),
            pendingAmount=self.sumFees(fees, lambda fee: (fee.status or "").lower() == "pending"),
            pendingFees=pendingFees,
        )

    def sumFees(self, fees: list[FeeDTO], predicate) -> Decimal:
        total = Decimal("0")
        for fee in fees:
            if predicate(fee) and fee.amount is not None:
                total += fee.amount
        return total
