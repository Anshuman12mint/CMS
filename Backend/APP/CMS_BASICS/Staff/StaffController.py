from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_BASICS.Staff.StaffDTO import StaffDTO
from APP.CMS_BASICS.Staff.StaffRepository import StaffRepository
from APP.CMS_BASICS.Staff.StaffService import StaffService

router = APIRouter(prefix="/api/staff", tags=["staff"], dependencies=[Depends(getCurrentUser)])


def getStaffService(session: Session = Depends(getDbSession)) -> StaffService:
    return StaffService(session, StaffRepository(session))


@router.get("", response_model=list[StaffDTO])
def getStaffMembers(staffService: StaffService = Depends(getStaffService)) -> list[StaffDTO]:
    return staffService.getAllStaff()


@router.get("/{staffId}", response_model=StaffDTO)
def getStaff(staffId: int, staffService: StaffService = Depends(getStaffService)) -> StaffDTO:
    return staffService.getStaff(staffId)


@router.post("", response_model=StaffDTO, status_code=status.HTTP_201_CREATED)
def createStaff(request: StaffDTO, staffService: StaffService = Depends(getStaffService)) -> StaffDTO:
    return staffService.createStaff(request)


@router.put("/{staffId}", response_model=StaffDTO)
def updateStaff(staffId: int, request: StaffDTO, staffService: StaffService = Depends(getStaffService)) -> StaffDTO:
    return staffService.updateStaff(staffId, request)


@router.delete("/{staffId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteStaff(staffId: int, staffService: StaffService = Depends(getStaffService)) -> Response:
    staffService.deleteStaff(staffId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
