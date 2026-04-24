from __future__ import annotations

from sqlalchemy.orm import Session

from APP.CMS_BASICS.Login_resister.JwtUtil import JwtUtil
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository


class JwtAuthenticationFilter:
    def __init__(self, jwtUtil: JwtUtil | None = None) -> None:
        self.jwtUtil = jwtUtil or JwtUtil()

    def authenticate(self, token: str, session: Session):
        if not token:
            return None
        try:
            username = self.jwtUtil.extractUsername(token)
            if not username:
                return None
            user = UserRepository(session).findByUsername(username)
            if user is None:
                return None
            if not self.jwtUtil.isTokenValid(token, user.username):
                return None
            return user
        except Exception:
            return None
