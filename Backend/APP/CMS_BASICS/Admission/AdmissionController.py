from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Admission.AdmissionDTO import AdmissionDTO
from APP.CMS_BASICS.Admission.AdmissionRepository import AdmissionRepository
from APP.CMS_BASICS.Admission.AdmissionService import AdmissionService
from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository

router = APIRouter(prefix="/api/admissions", tags=["admissions"], dependencies=[Depends(getCurrentUser)])


def getAdmissionService(session: Session = Depends(getDbSession)) -> AdmissionService:
    studentRepository = StudentRepository(session)
    return AdmissionService(
        session,
        AdmissionRepository(studentRepository),
        studentRepository,
        CourseRepository(session),
    )


@router.get("", response_model=list[AdmissionDTO])
def getAdmissions(admissionService: AdmissionService = Depends(getAdmissionService)) -> list[AdmissionDTO]:
    return admissionService.getAdmissions()


@router.get("/{studentId}", response_model=AdmissionDTO)
def getAdmission(studentId: int, admissionService: AdmissionService = Depends(getAdmissionService)) -> AdmissionDTO:
    return admissionService.getAdmission(studentId)


@router.post("", response_model=AdmissionDTO, status_code=status.HTTP_201_CREATED)
def createAdmission(request: AdmissionDTO, admissionService: AdmissionService = Depends(getAdmissionService)) -> AdmissionDTO:
    return admissionService.createAdmission(request)


@router.put("/{studentId}", response_model=AdmissionDTO)
def updateAdmission(studentId: int, request: AdmissionDTO, admissionService: AdmissionService = Depends(getAdmissionService)) -> AdmissionDTO:
    return admissionService.updateAdmission(studentId, request)


@router.delete("/{studentId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteAdmission(studentId: int, admissionService: AdmissionService = Depends(getAdmissionService)) -> Response:
    admissionService.deleteAdmission(studentId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
