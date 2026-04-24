from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.CMS_BASICS.fees.Fee import Fee
from APP.CMS_BASICS.fees.FeeDTO import FeeDTO
from APP.CMS_BASICS.fees.FeeRepository import FeeRepository
from APP.CMS_BASICS.Student.Student import Student
from APP.CMS_BASICS.Student.StudentRepository import StudentRepository
from APP.Utils.Validators import Validators


class FeeService:
    def __init__(self, session: Session, feeRepository: FeeRepository, studentRepository: StudentRepository) -> None:
        self.session = session
        self.feeRepository = feeRepository
        self.studentRepository = studentRepository

    def getFees(self, studentId: int | None) -> list[FeeDTO]:
        rows = self.feeRepository.findAllByOrderByDueDateDesc() if studentId is None else self.feeRepository.findByStudentStudentIdOrderByDueDateDesc(studentId)
        return [self.toDto(row) for row in rows]

    def getFee(self, feeId: int) -> FeeDTO:
        return self.toDto(self.findFee(feeId))

    def createFee(self, request: FeeDTO) -> FeeDTO:
        fee = Fee()
        fee.student = self.findStudent(request.studentId)
        fee.studentId = fee.student.studentId  # type: ignore[assignment]
        Validators.require(request.amount is not None, "amount is required")
        Validators.require(request.dueDate is not None, "dueDate is required")
        fee.amount = request.amount
        fee.status = Validators.normalizeRequiredChoice(request.status, Validators.FEE_STATUSES, "status")
        fee.dueDate = request.dueDate
        return self.toDto(self.feeRepository.save(fee))

    def updateFee(self, feeId: int, request: FeeDTO) -> FeeDTO:
        fee = self.findFee(feeId)
        fee.student = self.findStudent(request.studentId)
        fee.studentId = fee.student.studentId  # type: ignore[assignment]
        Validators.require(request.amount is not None, "amount is required")
        Validators.require(request.dueDate is not None, "dueDate is required")
        fee.amount = request.amount
        fee.status = Validators.normalizeRequiredChoice(request.status, Validators.FEE_STATUSES, "status")
        fee.dueDate = request.dueDate
        return self.toDto(self.feeRepository.save(fee))

    def deleteFee(self, feeId: int) -> None:
        self.feeRepository.delete(self.findFee(feeId))

    def findFee(self, feeId: int | None) -> Fee:
        fee = self.feeRepository.findById(feeId)
        if fee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee not found")
        return fee

    def findStudent(self, studentId: int | None) -> Student:
        student = self.studentRepository.findById(studentId)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def toDto(self, fee: Fee) -> FeeDTO:
        return FeeDTO(
            feeId=fee.feeId,
            studentId=fee.student.studentId if fee.student is not None else fee.studentId,
            amount=fee.amount,
            status=fee.status,
            dueDate=fee.dueDate,
        )
