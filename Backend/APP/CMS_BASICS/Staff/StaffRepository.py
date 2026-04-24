from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Staff.Staff import Staff


class StaffRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, staffId: int | None) -> Staff | None:
        return None if staffId is None else self.session.get(Staff, staffId)

    def findByEmailIgnoreCase(self, email: str | None) -> Staff | None:
        if email is None:
            return None
        return self.session.scalar(select(Staff).where(func.lower(Staff.email) == email.strip().lower()))

    def findAll(self) -> list[Staff]:
        return list(self.session.scalars(select(Staff)))

    def save(self, staff: Staff) -> Staff:
        self.session.add(staff)
        self.session.flush()
        self.session.refresh(staff)
        return staff

    def delete(self, staff: Staff) -> None:
        self.session.delete(staff)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Staff)) or 0)
