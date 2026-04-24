from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from APP.CMS_BASICS.Admission.AdmissionController import router as admissionRouter
from APP.CMS_BASICS.Attendance.AttendanceController import router as attendanceRouter
from APP.CMS_BASICS.Login_resister.AuthController import router as authRouter
from APP.Utils.Config.AppConfig import getSettings
from APP.Utils.Config.SecurityConfig import configureSecurity
from APP.CMS_BASICS.Course.CourseController import router as courseRouter
from APP.CMS_BASICS.dashbordbyusers.DashboardController import router as dashboardRouter
from APP.Utils.Database.BootstrapAdminInitializer import BootstrapAdminInitializer
from APP.Utils.Database.DatabaseConfig import initializeDatabase, sessionContext
from APP.Utils.Database.SampleDataInitializer import SampleDataInitializer
from APP.CMS_BASICS.fees.FeeController import router as feeRouter
from APP.CMS_BASICS.Marks.StudentMarkController import router as markRouter
from APP.CMS_extras.Communication.Meeting.MeetingController import router as meetingRouter
from APP.CMS_BASICS.Reports.ReportController import router as reportRouter
from APP.CMS_BASICS.Staff.StaffController import router as staffRouter
from APP.CMS_BASICS.Student.StudentController import router as studentRouter
from APP.CMS_BASICS.Subject.SubjectController import router as subjectRouter
from APP.CMS_BASICS.Teacher.TeacherController import router as teacherRouter
from APP.CMS_BASICS.Login_resister.UserController import router as userRouter


ROUTERS = (
    authRouter,
    userRouter,
    courseRouter,
    subjectRouter,
    studentRouter,
    admissionRouter,
    attendanceRouter,
    feeRouter,
    markRouter,
    staffRouter,
    teacherRouter,
    dashboardRouter,
    reportRouter,
    meetingRouter,
)


def initializeApplicationData() -> None:
    initializeDatabase()
    with sessionContext() as session:
        BootstrapAdminInitializer(session).run()
        SampleDataInitializer(session).run()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initializeApplicationData()
    yield


def createApp() -> FastAPI:
    app = FastAPI(title=getSettings().appName, lifespan=lifespan)
    configureSecurity(app)

    for router in ROUTERS:
        app.include_router(router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = createApp()


if __name__ == "__main__":
    import uvicorn

    settings = getSettings()
    uvicorn.run("MainApplication:app", host="0.0.0.0", port=settings.serverPort, reload=True)
