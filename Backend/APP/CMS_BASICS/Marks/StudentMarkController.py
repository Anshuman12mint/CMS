from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Marks.StudentMarkDTO import StudentMarkDTO
from APP.CMS_BASICS.Marks.StudentMarkRepository import StudentMarkRepository
from APP.CMS_BASICS.Marks.StudentMarkService import StudentMarkService
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository

router = APIRouter(prefix="/api/marks", tags=["marks"], dependencies=[Depends(getCurrentUser)])


def getStudentMarkService(session: Session = Depends(getDbSession)) -> StudentMarkService:
    return StudentMarkService(session, StudentMarkRepository(session), StudentRepository(session), SubjectRepository(session))


@router.get("", response_model=list[StudentMarkDTO])
def getMarks(studentId: int | None = Query(default=None), studentMarkService: StudentMarkService = Depends(getStudentMarkService)) -> list[StudentMarkDTO]:
    return studentMarkService.getMarks(studentId)


@router.get("/{markId}", response_model=StudentMarkDTO)
def getMark(markId: int, studentMarkService: StudentMarkService = Depends(getStudentMarkService)) -> StudentMarkDTO:
    return studentMarkService.getMark(markId)


@router.post("", response_model=StudentMarkDTO, status_code=status.HTTP_201_CREATED)
def createMark(request: StudentMarkDTO, studentMarkService: StudentMarkService = Depends(getStudentMarkService)) -> StudentMarkDTO:
    return studentMarkService.createMark(request)


@router.put("/{markId}", response_model=StudentMarkDTO)
def updateMark(markId: int, request: StudentMarkDTO, studentMarkService: StudentMarkService = Depends(getStudentMarkService)) -> StudentMarkDTO:
    return studentMarkService.updateMark(markId, request)


@router.delete("/{markId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteMark(markId: int, studentMarkService: StudentMarkService = Depends(getStudentMarkService)) -> Response:
    studentMarkService.deleteMark(markId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
