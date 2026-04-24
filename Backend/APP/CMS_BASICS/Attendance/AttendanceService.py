from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Attendance.Attendance import Attendance
from APP.CMS_BASICS.Attendance.AttendanceDTO import AttendanceDTO
from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.Utils.Validators import Validators


class AttendanceService:
    def __init__(self, session: Session, attendanceRepository: AttendanceRepository, studentRepository: StudentRepository) -> None:
        self.session = session
        self.attendanceRepository = attendanceRepository
        self.studentRepository = studentRepository

    def getAttendance(self, studentId: int | None) -> list[AttendanceDTO]:
        rows = (
            self.attendanceRepository.findAllByOrderByDateDesc()
            if studentId is None
            else self.attendanceRepository.findByStudentStudentIdOrderByDateDesc(studentId)
        )
        return [self.toDto(row) for row in rows]

    def getAttendanceById(self, attendanceId: int) -> AttendanceDTO:
        return self.toDto(self.findAttendance(attendanceId))

    def createAttendance(self, request: AttendanceDTO) -> AttendanceDTO:
        attendance = Attendance()
        attendance.student = self.findStudent(request.studentId)
        attendance.studentId = attendance.student.studentId  # type: ignore[assignment]
        Validators.require(request.date is not None, "date is required")
        attendance.date = request.date
        attendance.status = Validators.normalizeRequiredChoice(request.status, Validators.ATTENDANCE_STATUSES, "status")
        return self.toDto(self.attendanceRepository.save(attendance))

    def updateAttendance(self, attendanceId: int, request: AttendanceDTO) -> AttendanceDTO:
        attendance = self.findAttendance(attendanceId)
        attendance.student = self.findStudent(request.studentId)
        attendance.studentId = attendance.student.studentId  # type: ignore[assignment]
        Validators.require(request.date is not None, "date is required")
        attendance.date = request.date
        attendance.status = Validators.normalizeRequiredChoice(request.status, Validators.ATTENDANCE_STATUSES, "status")
        return self.toDto(self.attendanceRepository.save(attendance))

    def deleteAttendance(self, attendanceId: int) -> None:
        self.attendanceRepository.delete(self.findAttendance(attendanceId))

    def findAttendance(self, attendanceId: int | None) -> Attendance:
        attendance = self.attendanceRepository.findById(attendanceId)
        if attendance is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
        return attendance

    def findStudent(self, studentId: int | None) -> Student:
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def toDto(self, attendance: Attendance) -> AttendanceDTO:
        return AttendanceDTO(
            attendanceId=attendance.attendanceId,
            studentId=attendance.student.studentId if attendance.student is not None else attendance.studentId,
            date=attendance.date,
            status=attendance.status,
        )
