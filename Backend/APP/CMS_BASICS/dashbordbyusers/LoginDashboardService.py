from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Admission.AdmissionRepository import AdmissionRepository
from APP.CMS_BASICS.Admission.AdmissionService import AdmissionService
from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.CMS_BASICS.Attendance.AttendanceService import AttendanceService
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Course.CourseService import CourseService
from APP.CMS_BASICS.dashbordbyusers.DashboardService import DashboardService
from APP.CMS_BASICS.fees.FeeDTO import FeeDTO
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.fees.FeeService import FeeService
from APP.CMS_BASICS.Login_resister.User import User
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository
from APP.CMS_BASICS.Marks.StudentMarkService import StudentMarkService
from APP.CMS_BASICS.Staff.StaffRepository import StaffRepository
from APP.CMS_BASICS.Staff.StaffService import StaffService
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Student.StudentService import StudentService
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Subject.SubjectService import SubjectService
from APP.CMS_BASICS.Teacher.Teacher import Teacher
from APP.CMS_BASICS.Teacher.TeacherCourseRepository import TeacherCourseRepository
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Teacher.TeacherService import TeacherService
from APP.CMS_BASICS.Teacher.TeacherSubjectRepository import TeacherSubjectRepository


class LoginDashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.studentRepository = StudentRepository(session)
        self.teacherRepository = TeacherRepository(session)
        self.staffRepository = StaffRepository(session)
        self.courseRepository = CourseRepository(session)
        self.subjectRepository = SubjectRepository(session)
        self.userRepository = UserRepository(session)
        self.attendanceRepository = AttendanceRepository(session)
        self.feeRepository = FeeRepository(session)
        self.studentMarkRepository = StudentMarkRepository(session)
        self.teacherCourseRepository = TeacherCourseRepository(session)
        self.teacherSubjectRepository = TeacherSubjectRepository(session)

    def getDashboardForUser(self, user: User) -> dict[str, Any]:
        role = (user.role or "").strip().lower()
        if role == "student":
            return self.getStudentDashboard(user)
        if role == "teacher":
            return self.getTeacherDashboard(user)
        if role == "staff":
            return self.getStaffDashboard(user)
        if role == "admin":
            return self.getAdminDashboard()
        return {"type": "basic", "summary": self.dump(self.getDashboardSummary())}

    def getAdminDashboard(self) -> dict[str, Any]:
        return {
            "type": "admin",
            "summary": self.dump(self.getDashboardSummary()),
        }

    def getStaffDashboard(self, user: User) -> dict[str, Any]:
        staff = self.staffRepository.findByEmailIgnoreCase(user.email)
        staffProfile = StaffService(self.session, self.staffRepository).toDto(staff) if staff is not None else None
        return {
            "type": "staff",
            "staff": self.dump(staffProfile),
            "summary": self.dump(self.getDashboardSummary()),
        }

    def getStudentDashboard(self, user: User) -> dict[str, Any]:
        student = self.resolveStudent(user)
        if student is None:
            return {
                "type": "student",
                "student": None,
                "message": "No student profile is linked to this user.",
            }

        studentService = StudentService(self.session, self.studentRepository, self.courseRepository)
        attendanceService = AttendanceService(self.session, self.attendanceRepository, self.studentRepository)
        feeService = FeeService(self.session, self.feeRepository, self.studentRepository)
        markService = StudentMarkService(
            self.session,
            self.studentMarkRepository,
            self.studentRepository,
            self.subjectRepository,
        )

        attendance = attendanceService.getAttendance(student.studentId)
        fees = feeService.getFees(student.studentId)
        marks = markService.getMarks(student.studentId)
        pendingFees = [fee for fee in fees if self.matchesStatus(fee.status, "Pending")]

        return {
            "type": "student",
            "student": self.dump(studentService.toDto(student)),
            "quickStats": {
                "presentDays": sum(1 for item in attendance if self.matchesStatus(item.status, "Present")),
                "absentDays": sum(1 for item in attendance if self.matchesStatus(item.status, "Absent")),
                "totalAttendanceRecords": len(attendance),
                "totalFees": self.sumFees(fees),
                "paidFees": self.sumFees([fee for fee in fees if self.matchesStatus(fee.status, "Paid")]),
                "pendingFeeCount": len(pendingFees),
                "pendingFeesAmount": self.sumFees(pendingFees),
                "marksRecorded": len(marks),
            },
            "recentAttendance": self.dump(attendance[:5]),
            "recentFees": self.dump(fees[:5]),
            "pendingFees": self.dump(pendingFees[:5]),
            "recentMarks": self.dump(marks[:5]),
        }

    def getTeacherDashboard(self, user: User) -> dict[str, Any]:
        teacher = self.teacherRepository.findByEmailIgnoreCase(user.email)
        if teacher is None:
            return {
                "type": "teacher",
                "teacher": None,
                "message": "No teacher profile is linked to this user email.",
            }

        teacherService = self.createTeacherService()
        courseService = CourseService(self.session, self.courseRepository)
        subjectService = SubjectService(self.session, self.subjectRepository, self.courseRepository)
        teacherDto = teacherService.toDto(teacher)
        courses = [courseService.getCourse(courseCode) for courseCode in teacherDto.courseCodes]
        subjects = [subjectService.getSubject(subjectId) for subjectId in teacherDto.subjectIds]
        studentsByCourse = {
            courseCode: len(self.studentRepository.findByCourseCodeOrderByAdmissionDateDesc(courseCode))
            for courseCode in teacherDto.courseCodes
        }

        return {
            "type": "teacher",
            "teacher": self.dump(teacherDto),
            "quickStats": {
                "assignedCourses": len(teacherDto.courseCodes),
                "assignedSubjects": len(teacherDto.subjectIds),
                "studentsInAssignedCourses": sum(studentsByCourse.values()),
            },
            "courses": self.dump(courses),
            "subjects": self.dump(subjects),
            "studentsByCourse": studentsByCourse,
        }

    def getDashboardSummary(self):
        admissionService = AdmissionService(
            self.session,
            AdmissionRepository(self.studentRepository),
            self.studentRepository,
            self.courseRepository,
        )
        return DashboardService(
            self.session,
            self.studentRepository,
            self.teacherRepository,
            self.staffRepository,
            self.courseRepository,
            self.subjectRepository,
            self.userRepository,
            self.attendanceRepository,
            self.feeRepository,
            self.studentMarkRepository,
            admissionService,
        ).getSummary()

    def createTeacherService(self) -> TeacherService:
        return TeacherService(
            self.session,
            self.teacherRepository,
            self.courseRepository,
            self.subjectRepository,
            self.teacherCourseRepository,
            self.teacherSubjectRepository,
        )

    def resolveStudent(self, user: User) -> Student | None:
        if user.student is not None:
            return user.student
        student = self.studentRepository.findById(user.studentId)
        if student is not None:
            return student
        return self.studentRepository.findByEmailIgnoreCase(user.email)

    def matchesStatus(self, value: str | None, expected: str) -> bool:
        return (value or "").strip().lower() == expected.lower()

    def sumFees(self, fees: list[FeeDTO]) -> Decimal:
        total = Decimal("0")
        for fee in fees:
            if fee.amount is not None:
                total += fee.amount
        return total

    def dump(self, value):
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, list):
            return [self.dump(item) for item in value]
        if isinstance(value, dict):
            return {key: self.dump(item) for key, item in value.items()}
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, date | datetime):
            return value.isoformat()
        return value
