from __future__ import annotations

from sqlalchemy.orm import Session

from APP.Utils.Config.AppConfig import getSettings
from APP.Utils.Config.SecurityConfig import hashPassword
from APP.CMS_BASICS.Login_resister.User import User
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.Utils.Helpers import Helpers


class BootstrapAdminInitializer:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.userRepository = UserRepository(session)
        self.settings = getSettings()

    def run(self) -> None:
        if not self.settings.bootstrapAdminEnabled or self.userRepository.count() > 0:
            return

        username = Helpers.trimToNull(self.settings.bootstrapAdminUsername)
        password = Helpers.trimToNull(self.settings.bootstrapAdminPassword)
        email = Helpers.trimToNull(self.settings.bootstrapAdminEmail)
        if not username or not password or not email:
            raise ValueError("Bootstrap admin properties must not be blank")

        admin = User()
        admin.username = username
        admin.passwordHash = hashPassword(password)
        admin.email = email.lower()
        admin.role = "Admin"
        self.userRepository.save(admin)
