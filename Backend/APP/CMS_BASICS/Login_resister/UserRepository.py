from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from APP.CMS_BASICS.Login_resister.User import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def findById(self, userId: int | None) -> User | None:
        return None if userId is None else self.session.get(User, userId)

    def findByUsername(self, username: str | None) -> User | None:
        if username is None:
            return None
        return self.session.scalar(select(User).where(User.username == username))

    def findAllByOrderByCreatedAtDesc(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.createdAt.desc())))

    def existsByUsername(self, username: str | None) -> bool:
        if username is None:
            return False
        return self.session.scalar(select(func.count()).select_from(User).where(User.username == username)) > 0

    def existsByEmail(self, email: str | None) -> bool:
        if email is None:
            return False
        return self.session.scalar(select(func.count()).select_from(User).where(func.lower(User.email) == email.lower())) > 0

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(User)) or 0)
