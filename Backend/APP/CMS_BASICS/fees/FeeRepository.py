from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.fees.Fee import Fee


class FeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, feeId: int | None) -> Fee | None:
        return None if feeId is None else self.session.get(Fee, feeId)

    def findByStudentStudentIdOrderByDueDateDesc(self, studentId: int) -> list[Fee]:
        return list(self.session.scalars(select(Fee).where(Fee.studentId == studentId).order_by(Fee.dueDate.desc())))

    def findAllByOrderByDueDateDesc(self) -> list[Fee]:
        return list(self.session.scalars(select(Fee).order_by(Fee.dueDate.desc())))

    def save(self, fee: Fee) -> Fee:
        self.session.add(fee)
        self.session.flush()
        self.session.refresh(fee)
        return fee

    def saveAll(self, fees: list[Fee]) -> list[Fee]:
        self.session.add_all(fees)
        self.session.flush()
        return fees

    def delete(self, fee: Fee) -> None:
        self.session.delete(fee)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Fee)) or 0)

    def countByStatusIgnoreCase(self, status: str) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Fee).where(func.lower(Fee.status) == status.lower())) or 0)

    def sumPendingAmount(self) -> Decimal:
        value = self.session.scalar(select(func.coalesce(func.sum(Fee.amount), 0)).where(func.lower(Fee.status) == "pending"))
        return Decimal(value or 0)
