from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from APP.Utils.Config.AppConfig import getSettings
from APP.Utils.Config.SecurityConfig import hashPassword
from APP.CMS_BASICS.Course.Course import Course
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Subject.Subject import Subject
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Teacher.Teacher import Teacher
from APP.CMS_BASICS.Teacher.TeacherCourse import TeacherCourse
from APP.CMS_BASICS.Teacher.TeacherCourseId import TeacherCourseId
from APP.CMS_BASICS.Teacher.TeacherCourseRepository import TeacherCourseRepository
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Teacher.TeacherSubject import TeacherSubject
from APP.CMS_BASICS.Teacher.TeacherSubjectId import TeacherSubjectId
from APP.CMS_BASICS.Teacher.TeacherSubjectRepository import TeacherSubjectRepository
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Login_resister.User import User
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.CMS_BASICS.Attendance.Attendance import Attendance
from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.CMS_BASICS.fees.Fee import Fee
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.Marks.StudentMark import StudentMark
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository


class SampleDataInitializer:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = getSettings()
        self.courseRepository = CourseRepository(session)
        self.subjectRepository = SubjectRepository(session)
        self.teacherRepository = TeacherRepository(session)
        self.teacherCourseRepository = TeacherCourseRepository(session)
        self.teacherSubjectRepository = TeacherSubjectRepository(session)
        self.studentRepository = StudentRepository(session)
        self.userRepository = UserRepository(session)
        self.attendanceRepository = AttendanceRepository(session)
        self.feeRepository = FeeRepository(session)
        self.studentMarkRepository = StudentMarkRepository(session)

    def run(self) -> None:
        if not self.settings.bootstrapSampleDataEnabled or self.hasDomainData():
            return

        bca = self.saveCourse(
            "BCA101",
            "Bachelor of Computer Applications",
            "Three-year undergraduate course focused on computer science and programming.",
        )
        self.saveCourse(
            "BSC102",
            "Bachelor of Science",
            "Undergraduate science program with multiple streams.",
        )

        dbms = self.saveSubject("Database Management Systems", "DBMS01", bca.courseCode, "Relational databases and SQL.")
        os = self.saveSubject("Operating Systems", "OS01", bca.courseCode, "Concepts of operating systems.")
        cn = self.saveSubject("Computer Networks", "CN01", bca.courseCode, "Networking and communication systems.")

        teacher = Teacher()
        teacher.firstName = "Rajesh"
        teacher.lastName = "Kumar"
        teacher.dob = date(1985, 3, 12)
        teacher.gender = "Male"
        teacher.phoneNumber = "9876543210"
        teacher.email = "rajesh.kumar@example.com"
        teacher.hireDate = date(2015, 7, 10)
        teacher.department = "Computer Science"
        teacher.address = "Haridwar, Uttarakhand"
        teacher.qualification = "MCA"
        teacher.salary = Decimal("60000.00")
        self.teacherRepository.save(teacher)

        self.teacherCourseRepository.save(self.teacherCourse(teacher, bca))
        self.teacherSubjectRepository.saveAll([
            self.teacherSubject(teacher, dbms),
            self.teacherSubject(teacher, os),
            self.teacherSubject(teacher, cn),
        ])

        rohit = Student()
        rohit.firstName = "Rohit"
        rohit.lastName = "Verma"
        rohit.dob = date(2004, 8, 22)
        rohit.gender = "Male"
        rohit.phoneNumber = "9898989898"
        rohit.email = "rohit.verma@example.com"
        rohit.courseCode = bca.courseCode
        rohit.admissionDate = date(2022, 7, 1)
        rohit.address = "Dehradun, Uttarakhand"
        rohit.guardianName = "Amit Verma"
        rohit.guardianContact = "9823456789"
        rohit.bloodGroup = "B+"
        self.studentRepository.save(rohit)

        anjali = Student()
        anjali.firstName = "Anjali"
        anjali.lastName = "Sharma"
        anjali.dob = date(2003, 11, 5)
        anjali.gender = "Female"
        anjali.phoneNumber = "9876501234"
        anjali.email = "anjali.sharma@example.com"
        anjali.courseCode = bca.courseCode
        anjali.admissionDate = date(2022, 7, 1)
        anjali.address = "Rishikesh, Uttarakhand"
        anjali.guardianName = "Pooja Sharma"
        anjali.guardianContact = "9812345678"
        anjali.bloodGroup = "O+"
        self.studentRepository.save(anjali)

        self.createUser("rajesh", "teacher123", "rajesh.kumar@example.com", "Teacher", None)
        self.createUser("rohit", "student123", "rohit.verma@example.com", "Student", rohit)
        self.createUser("anjali", "student123", "anjali.sharma@example.com", "Student", anjali)

        self.attendanceRepository.saveAll([
            self.attendance(rohit, date(2025, 10, 10), "Present"),
            self.attendance(rohit, date(2025, 10, 11), "Absent"),
            self.attendance(anjali, date(2025, 10, 10), "Present"),
            self.attendance(anjali, date(2025, 10, 11), "Present"),
        ])

        self.feeRepository.saveAll([
            self.fee(rohit, "25000.00", "Paid", date(2025, 9, 1)),
            self.fee(anjali, "25000.00", "Pending", date(2025, 9, 1)),
        ])

        self.studentMarkRepository.saveAll([
            self.mark(rohit, dbms, 1, "Midterm", "42.00", "50.00", "A", date(2025, 9, 15)),
            self.mark(rohit, os, 1, "Final", "85.00", "100.00", "A", date(2025, 10, 1)),
            self.mark(anjali, dbms, 1, "Midterm", "38.00", "50.00", "B", date(2025, 9, 15)),
            self.mark(anjali, cn, 1, "Final", "78.00", "100.00", "B", date(2025, 10, 1)),
        ])

    def hasDomainData(self) -> bool:
        return any([
            self.courseRepository.count() > 0,
            self.subjectRepository.count() > 0,
            self.teacherRepository.count() > 0,
            self.studentRepository.count() > 0,
            self.attendanceRepository.count() > 0,
            self.feeRepository.count() > 0,
            self.studentMarkRepository.count() > 0,
            self.teacherCourseRepository.count() > 0,
            self.teacherSubjectRepository.count() > 0,
        ])

    def saveCourse(self, code: str, name: str, description: str) -> Course:
        course = Course()
        course.courseCode = code
        course.courseName = name
        course.courseDescription = description
        return self.courseRepository.save(course)

    def saveSubject(self, name: str, code: str, courseCode: str, description: str) -> Subject:
        subject = Subject()
        subject.subjectName = name
        subject.subjectCode = code
        subject.courseCode = courseCode
        subject.subjectDescription = description
        return self.subjectRepository.save(subject)

    def createUser(self, username: str, rawPassword: str, email: str, role: str, student: Student | None) -> None:
        if self.userRepository.findByUsername(username) is not None:
            return
        user = User()
        user.username = username
        user.passwordHash = hashPassword(rawPassword)
        user.email = email.lower()
        user.role = role
        user.student = student
        self.userRepository.save(user)

    def teacherCourse(self, teacher: Teacher, course: Course) -> TeacherCourse:
        assignment = TeacherCourse()
        assignment.id = TeacherCourseId(teacher.teacherId, course.courseCode)
        assignment.teacher = teacher
        assignment.course = course
        return assignment

    def teacherSubject(self, teacher: Teacher, subject: Subject) -> TeacherSubject:
        assignment = TeacherSubject()
        assignment.id = TeacherSubjectId(teacher.teacherId, subject.subjectId)
        assignment.teacher = teacher
        assignment.subject = subject
        return assignment

    def attendance(self, student: Student, attendanceDate: date, status: str) -> Attendance:
        attendance = Attendance()
        attendance.student = student
        attendance.date = attendanceDate
        attendance.status = status
        return attendance

    def fee(self, student: Student, amount: str, status: str, dueDate: date) -> Fee:
        fee = Fee()
        fee.student = student
        fee.amount = Decimal(amount)
        fee.status = status
        fee.dueDate = dueDate
        return fee

    def mark(
        self,
        student: Student,
        subject: Subject,
        semester: int,
        examType: str,
        marksObtained: str,
        maxMarks: str,
        grade: str,
        examDate: date,
    ) -> StudentMark:
        mark = StudentMark()
        mark.student = student
        mark.subject = subject
        mark.semester = semester
        mark.examType = examType
        mark.marksObtained = Decimal(marksObtained)
        mark.maxMarks = Decimal(maxMarks)
        mark.grade = grade
        mark.examDate = examDate
        return mark
