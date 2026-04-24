from __future__ import annotations

from pydantic import BaseModel


class MeetingMessageRequest(BaseModel):
    messageText: str
