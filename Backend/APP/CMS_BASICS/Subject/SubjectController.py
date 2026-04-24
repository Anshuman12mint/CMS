from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Subject.SubjectDTO import SubjectDTO
from APP.CMS_BASICS.Subject.SubjectRepository import SubjectRepository
from APP.CMS_BASICS.Subject.SubjectService import SubjectService

router = APIRouter(prefix="/api/subjects", tags=["subjects"], dependencies=[Depends(getCurrentUser)])


def getSubjectService(session: Session = Depends(getDbSession)) -> SubjectService:
    return SubjectService(session, SubjectRepository(session), CourseRepository(session))


@router.get("", response_model=list[SubjectDTO])
def getSubjects(courseCode: str | None = Query(default=None), subjectService: SubjectService = Depends(getSubjectService)) -> list[SubjectDTO]:
    return subjectService.getAllSubjects(courseCode)


@router.get("/{subjectId}", response_model=SubjectDTO)
def getSubject(subjectId: int, subjectService: SubjectService = Depends(getSubjectService)) -> SubjectDTO:
    return subjectService.getSubject(subjectId)


@router.post("", response_model=SubjectDTO, status_code=status.HTTP_201_CREATED)
def createSubject(request: SubjectDTO, subjectService: SubjectService = Depends(getSubjectService)) -> SubjectDTO:
    return subjectService.createSubject(request)


@router.put("/{subjectId}", response_model=SubjectDTO)
def updateSubject(subjectId: int, request: SubjectDTO, subjectService: SubjectService = Depends(getSubjectService)) -> SubjectDTO:
    return subjectService.updateSubject(subjectId, request)


@router.delete("/{subjectId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteSubject(subjectId: int, subjectService: SubjectService = Depends(getSubjectService)) -> Response:
    subjectService.deleteSubject(subjectId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
