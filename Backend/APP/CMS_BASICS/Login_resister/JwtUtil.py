from __future__ import annotations

from datetime import timedelta

import jwt

from APP.Utils.Config.AppConfig import getSettings, utcNow


class JwtUtil:
    def __init__(self) -> None:
        self.settings = getSettings()

    def generateToken(self, username: str, role: str) -> str:
        now = utcNow()
        payload = {
            "sub": username,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.settings.jwtExpirationMinutes)).timestamp()),
        }
        return jwt.encode(payload, self.settings.jwtSecret, algorithm="HS256")

    def extractUsername(self, token: str) -> str:
        return self.parseClaims(token).get("sub", "")

    def isTokenValid(self, token: str, expectedUsername: str) -> bool:
        claims = self.parseClaims(token)
        return claims.get("sub") == expectedUsername

    def parseClaims(self, token: str) -> dict:
        return jwt.decode(token, self.settings.jwtSecret, algorithms=["HS256"])
