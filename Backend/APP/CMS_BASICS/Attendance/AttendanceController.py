from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Attendance.AttendanceDTO import AttendanceDTO
from APP.CMS_BASICS.Attendance.AttendanceRepository import AttendanceRepository
from APP.CMS_BASICS.Attendance.AttendanceService import AttendanceService
from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository

router = APIRouter(prefix="/api/attendance", tags=["attendance"], dependencies=[Depends(getCurrentUser)])


def getAttendanceService(session: Session = Depends(getDbSession)) -> AttendanceService:
    return AttendanceService(session, AttendanceRepository(session), StudentRepository(session))


@router.get("", response_model=list[AttendanceDTO])
def getAttendance(studentId: int | None = Query(default=None), attendanceService: AttendanceService = Depends(getAttendanceService)) -> list[AttendanceDTO]:
    return attendanceService.getAttendance(studentId)


@router.get("/{attendanceId}", response_model=AttendanceDTO)
def getAttendanceById(attendanceId: int, attendanceService: AttendanceService = Depends(getAttendanceService)) -> AttendanceDTO:
    return attendanceService.getAttendanceById(attendanceId)


@router.post("", response_model=AttendanceDTO, status_code=status.HTTP_201_CREATED)
def createAttendance(request: AttendanceDTO, attendanceService: AttendanceService = Depends(getAttendanceService)) -> AttendanceDTO:
    return attendanceService.createAttendance(request)


@router.put("/{attendanceId}", response_model=AttendanceDTO)
def updateAttendance(attendanceId: int, request: AttendanceDTO, attendanceService: AttendanceService = Depends(getAttendanceService)) -> AttendanceDTO:
    return attendanceService.updateAttendance(attendanceId, request)


@router.delete("/{attendanceId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteAttendance(attendanceId: int, attendanceService: AttendanceService = Depends(getAttendanceService)) -> Response:
    attendanceService.deleteAttendance(attendanceId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
