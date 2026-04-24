from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Teacher.Teacher import Teacher
from APP.CMS_BASICS.Teacher.TeacherCourse import TeacherCourse
from APP.CMS_BASICS.Teacher.TeacherCourseId import TeacherCourseId
from APP.CMS_BASICS.Teacher.TeacherCourseRepository import TeacherCourseRepository
from APP.CMS_BASICS.Teacher.TeacherDTO import TeacherDTO
from APP.CMS_BASICS.Teacher.TeacherRepository import TeacherRepository
from APP.CMS_BASICS.Teacher.TeacherSubject import TeacherSubject
from APP.CMS_BASICS.Teacher.TeacherSubjectId import TeacherSubjectId
from APP.CMS_BASICS.Teacher.TeacherSubjectRepository import TeacherSubjectRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class TeacherService:
    def __init__(
        self,
        session: Session,
        teacherRepository: TeacherRepository,
        courseRepository: CourseRepository,
        subjectRepository: SubjectRepository,
        teacherCourseRepository: TeacherCourseRepository,
        teacherSubjectRepository: TeacherSubjectRepository,
    ) -> None:
        self.session = session
        self.teacherRepository = teacherRepository
        self.courseRepository = courseRepository
        self.subjectRepository = subjectRepository
        self.teacherCourseRepository = teacherCourseRepository
        self.teacherSubjectRepository = teacherSubjectRepository

    def getAllTeachers(self) -> list[TeacherDTO]:
        return [self.toDto(teacher) for teacher in self.teacherRepository.findAll()]

    def getTeacher(self, teacherId: int) -> TeacherDTO:
        return self.toDto(self.findTeacher(teacherId))

    def createTeacher(self, request: TeacherDTO) -> TeacherDTO:
        teacher = Teacher()
        self.apply(teacher, request)
        savedTeacher = self.teacherRepository.save(teacher)
        self.syncAssignments(savedTeacher, request.courseCodes, request.subjectIds)
        return self.getTeacher(savedTeacher.teacherId)

    def updateTeacher(self, teacherId: int, request: TeacherDTO) -> TeacherDTO:
        teacher = self.findTeacher(teacherId)
        self.apply(teacher, request)
        self.teacherRepository.save(teacher)
        if request.courseCodes is not None or request.subjectIds is not None:
            self.syncAssignments(teacher, request.courseCodes, request.subjectIds)
        return self.getTeacher(teacherId)

    def deleteTeacher(self, teacherId: int) -> None:
        self.teacherRepository.delete(self.findTeacher(teacherId))

    def replaceCourses(self, teacherId: int, courseCodes: list[str] | None) -> TeacherDTO:
        teacher = self.findTeacher(teacherId)
        self.syncCourses(teacher, courseCodes)
        return self.getTeacher(teacherId)

    def replaceSubjects(self, teacherId: int, subjectIds: list[int] | None) -> TeacherDTO:
        teacher = self.findTeacher(teacherId)
        self.syncSubjects(teacher, subjectIds)
        return self.getTeacher(teacherId)

    def findTeacher(self, teacherId: int | None) -> Teacher:
        teacher = self.teacherRepository.findById(teacherId)
        if teacher is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
        return teacher

    def apply(self, teacher: Teacher, request: TeacherDTO) -> None:
        Validators.requireText(request.firstName, "firstName")
        Validators.requireText(request.lastName, "lastName")
        Validators.require(request.dob is not None, "dob is required")
        Validators.require(request.hireDate is not None, "hireDate is required")
        Validators.requireText(request.phoneNumber, "phoneNumber")
        Validators.requireText(request.email, "email")

        teacher.firstName = Helpers.trimToNull(request.firstName)  # type: ignore[assignment]
        teacher.lastName = Helpers.trimToNull(request.lastName)  # type: ignore[assignment]
        teacher.dob = request.dob  # type: ignore[assignment]
        teacher.gender = Validators.normalizeRequiredChoice(request.gender, Validators.GENDERS, "gender")
        teacher.phoneNumber = Helpers.trimToNull(request.phoneNumber)  # type: ignore[assignment]
        teacher.email = Helpers.trimToNull(request.email)  # type: ignore[assignment]
        teacher.hireDate = request.hireDate  # type: ignore[assignment]
        teacher.department = Helpers.trimToNull(request.department)
        teacher.address = Helpers.trimToNull(request.address)
        teacher.qualification = Helpers.trimToNull(request.qualification)
        teacher.salary = request.salary

    def toDto(self, teacher: Teacher) -> TeacherDTO:
        courseCodes = [assignment.course.courseCode for assignment in self.teacherCourseRepository.findByTeacherTeacherId(teacher.teacherId)]
        subjectIds = [assignment.subject.subjectId for assignment in self.teacherSubjectRepository.findByTeacherTeacherId(teacher.teacherId)]
        return TeacherDTO(
            teacherId=teacher.teacherId,
            firstName=teacher.firstName,
            lastName=teacher.lastName,
            dob=teacher.dob,
            gender=teacher.gender,
            phoneNumber=teacher.phoneNumber,
            email=teacher.email,
            hireDate=teacher.hireDate,
            department=teacher.department,
            address=teacher.address,
            qualification=teacher.qualification,
            salary=teacher.salary,
            createdAt=teacher.createdAt,
            courseCodes=courseCodes,
            subjectIds=subjectIds,
        )

    def syncAssignments(self, teacher: Teacher, courseCodes: list[str] | None, subjectIds: list[int] | None) -> None:
        if courseCodes is not None:
            self.syncCourses(teacher, courseCodes)
        if subjectIds is not None:
            self.syncSubjects(teacher, subjectIds)

    def syncCourses(self, teacher: Teacher, courseCodes: list[str] | None) -> None:
        self.teacherCourseRepository.deleteByTeacherTeacherId(teacher.teacherId)
        assignments: list[TeacherCourse] = []
        for courseCode in Helpers.distinctList(courseCodes):
            course = self.courseRepository.findById(courseCode)
            if course is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            assignment = TeacherCourse()
            assignment.id = TeacherCourseId(teacher.teacherId, course.courseCode)
            assignment.teacher = teacher
            assignment.course = course
            assignments.append(assignment)
        self.teacherCourseRepository.saveAll(assignments)

    def syncSubjects(self, teacher: Teacher, subjectIds: list[int] | None) -> None:
        self.teacherSubjectRepository.deleteByTeacherTeacherId(teacher.teacherId)
        assignments: list[TeacherSubject] = []
        for subjectId in Helpers.distinctList(subjectIds):
            subject = self.subjectRepository.findById(subjectId)
            if subject is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
            assignment = TeacherSubject()
            assignment.id = TeacherSubjectId(teacher.teacherId, subject.subjectId)
            assignment.teacher = teacher
            assignment.subject = subject
            assignments.append(assignment)
        self.teacherSubjectRepository.saveAll(assignments)
