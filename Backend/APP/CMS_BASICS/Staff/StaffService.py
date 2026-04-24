from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Staff.Staff import Staff
from APP.CMS_BASICS.Staff.StaffDTO import StaffDTO
from APP.CMS_BASICS.Staff.StaffRepository import StaffRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class StaffService:
    def __init__(self, session: Session, staffRepository: StaffRepository) -> None:
        self.session = session
        self.staffRepository = staffRepository

    def getAllStaff(self) -> list[StaffDTO]:
        return [self.toDto(staff) for staff in self.staffRepository.findAll()]

    def getStaff(self, staffId: int) -> StaffDTO:
        return self.toDto(self.findStaff(staffId))

    def createStaff(self, request: StaffDTO) -> StaffDTO:
        staff = Staff()
        self.apply(staff, request)
        return self.toDto(self.staffRepository.save(staff))

    def updateStaff(self, staffId: int, request: StaffDTO) -> StaffDTO:
        staff = self.findStaff(staffId)
        self.apply(staff, request)
        return self.toDto(self.staffRepository.save(staff))

    def deleteStaff(self, staffId: int) -> None:
        self.staffRepository.delete(self.findStaff(staffId))

    def findStaff(self, staffId: int | None) -> Staff:
        staff = self.staffRepository.findById(staffId)
        if staff is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
        return staff

    def apply(self, staff: Staff, request: StaffDTO) -> None:
        Validators.requireText(request.firstName, "firstName")
        Validators.requireText(request.lastName, "lastName")
        Validators.require(request.dob is not None, "dob is required")
        Validators.require(request.hireDate is not None, "hireDate is required")
        Validators.requireText(request.phoneNumber, "phoneNumber")
        Validators.requireText(request.email, "email")

        staff.firstName = Helpers.trimToNull(request.firstName)  # type: ignore[assignment]
        staff.lastName = Helpers.trimToNull(request.lastName)  # type: ignore[assignment]
        staff.dob = request.dob  # type: ignore[assignment]
        staff.gender = Validators.normalizeRequiredChoice(request.gender, Validators.GENDERS, "gender")
        staff.phoneNumber = Helpers.trimToNull(request.phoneNumber)  # type: ignore[assignment]
        staff.email = Helpers.trimToNull(request.email)  # type: ignore[assignment]
        staff.hireDate = request.hireDate  # type: ignore[assignment]
        staff.role = Validators.normalizeRequiredChoice(request.role, Validators.STAFF_ROLES, "role")
        staff.department = Helpers.trimToNull(request.department)
        staff.address = Helpers.trimToNull(request.address)
        staff.salary = request.salary

    def toDto(self, staff: Staff) -> StaffDTO:
        return StaffDTO(
            staffId=staff.staffId,
            firstName=staff.firstName,
            lastName=staff.lastName,
            dob=staff.dob,
            gender=staff.gender,
            phoneNumber=staff.phoneNumber,
            email=staff.email,
            hireDate=staff.hireDate,
            role=staff.role,
            department=staff.department,
            address=staff.address,
            salary=staff.salary,
            createdAt=staff.createdAt,
        )
