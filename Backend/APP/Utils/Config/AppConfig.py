from __future__ import annotations

import re
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    appName: str = "college-management-backend"
    serverPort: int = Field(default=8000, validation_alias="SERVER_PORT")
    dbUrl: str = Field(default="jdbc:mysql://localhost:3306/collegemanagement_system", validation_alias="DB_URL")
    dbUsername: str = Field(default="root", validation_alias="DB_USERNAME")
    dbPassword: str = Field(default="", validation_alias="DB_PASSWORD")
    jwtSecret: str = Field(
        default="change-this-secret-key-change-this-secret-key",
        validation_alias="JWT_SECRET",
    )
    jwtExpirationMinutes: int = Field(default=120, validation_alias="JWT_EXPIRATION_MINUTES")
    corsAllowedOriginPatterns: str = Field(
        default="*",
        validation_alias="CORS_ALLOWED_ORIGIN_PATTERNS",
    )
    meetingsProvider: str = Field(default="Jitsi", validation_alias="MEETINGS_PROVIDER")
    meetingsJitsiBaseUrl: str = Field(default="https://meet.jit.si", validation_alias="MEETINGS_JITSI_BASE_URL")
    bootstrapAdminEnabled: bool = Field(default=True, validation_alias="BOOTSTRAP_ADMIN_ENABLED")
    bootstrapAdminUsername: str = Field(default="admin", validation_alias="BOOTSTRAP_ADMIN_USERNAME")
    bootstrapAdminPassword: str = Field(default="admin123", validation_alias="BOOTSTRAP_ADMIN_PASSWORD")
    bootstrapAdminEmail: str = Field(default="admin@college.com", validation_alias="BOOTSTRAP_ADMIN_EMAIL")
    bootstrapSampleDataEnabled: bool = Field(default=True, validation_alias="BOOTSTRAP_SAMPLE_DATA_ENABLED")

    @property
    def databaseUrl(self) -> str:
        raw = self.dbUrl.strip()
        if raw.startswith("jdbc:mysql://"):
            host_and_db = raw.removeprefix("jdbc:mysql://")
            auth = quote_plus(self.dbUsername)
            if self.dbPassword:
                auth = f"{auth}:{quote_plus(self.dbPassword)}"
            return f"mysql+pymysql://{auth}@{host_and_db}"
        if raw.startswith("mysql://"):
            return raw.replace("mysql://", "mysql+pymysql://", 1)
        return raw

    @property
    def allowedOriginRegex(self) -> str | None:
        patterns = [item.strip() for item in self.corsAllowedOriginPatterns.split(",") if item.strip()]
        if not patterns:
            return None
        escaped = [re.escape(item).replace("\\*", ".*") for item in patterns]
        return "^(" + "|".join(escaped) + ")$"


@lru_cache(maxsize=1)
def getSettings() -> Settings:
    return Settings()


def utcNow() -> datetime:
    return datetime.now(timezone.utc)
