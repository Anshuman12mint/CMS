from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from APP.Utils.Config.AppConfig import getSettings


class Base(DeclarativeBase):
    pass


engine = create_engine(getSettings().databaseUrl, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def importModels() -> None:
    from APP.CMS_BASICS.Attendance.Attendance import Attendance  # noqa: F401
    from APP.CMS_BASICS.Course.Course import Course  # noqa: F401
    from APP.CMS_BASICS.fees.Fee import Fee  # noqa: F401
    from APP.CMS_BASICS.Marks.StudentMark import StudentMark  # noqa: F401
    from APP.CMS_extras.Communication.Meeting.Meeting import Meeting  # noqa: F401
    from APP.CMS_extras.Communication.Messages.MeetingMessage import MeetingMessage  # noqa: F401
    from APP.CMS_extras.Communication.Meeting.MeetingParticipant import MeetingParticipant  # noqa: F401
    from APP.CMS_BASICS.Staff.Staff import Staff  # noqa: F401
    from APP.CMS_BASICS.Student.Student import Student  # noqa: F401
    from APP.CMS_BASICS.Subject.Subject import Subject  # noqa: F401
    from APP.CMS_BASICS.Teacher.Teacher import Teacher  # noqa: F401
    from APP.CMS_BASICS.Teacher.TeacherCourse import TeacherCourse  # noqa: F401
    from APP.CMS_BASICS.Teacher.TeacherSubject import TeacherSubject  # noqa: F401
    from APP.CMS_BASICS.Login_resister.User import User  # noqa: F401


def initializeDatabase() -> None:
    importModels()
    Base.metadata.create_all(bind=engine)


def getDbSession() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def sessionContext() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
