from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.fees.FeeDTO import FeeDTO
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.fees.FeeService import FeeService
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository

router = APIRouter(prefix="/api/fees", tags=["fees"], dependencies=[Depends(getCurrentUser)])


def getFeeService(session: Session = Depends(getDbSession)) -> FeeService:
    return FeeService(session, FeeRepository(session), StudentRepository(session))


@router.get("", response_model=list[FeeDTO])
def getFees(studentId: int | None = Query(default=None), feeService: FeeService = Depends(getFeeService)) -> list[FeeDTO]:
    return feeService.getFees(studentId)


@router.get("/{feeId}", response_model=FeeDTO)
def getFee(feeId: int, feeService: FeeService = Depends(getFeeService)) -> FeeDTO:
    return feeService.getFee(feeId)


@router.post("", response_model=FeeDTO, status_code=status.HTTP_201_CREATED)
def createFee(request: FeeDTO, feeService: FeeService = Depends(getFeeService)) -> FeeDTO:
    return feeService.createFee(request)


@router.put("/{feeId}", response_model=FeeDTO)
def updateFee(feeId: int, request: FeeDTO, feeService: FeeService = Depends(getFeeService)) -> FeeDTO:
    return feeService.updateFee(feeId, request)


@router.delete("/{feeId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteFee(feeId: int, feeService: FeeService = Depends(getFeeService)) -> Response:
    feeService.deleteFee(feeId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
