from __future__ import annotations

from typing import Iterable, TypeVar

T = TypeVar("T")


class Helpers:
    @staticmethod
    def fullName(firstName: str | None, lastName: str | None) -> str:
        return " ".join(part.strip() for part in (firstName, lastName) if part and part.strip())

    @staticmethod
    def trimToNull(value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @staticmethod
    def distinctList(values: Iterable[T] | None) -> list[T]:
        if values is None:
            return []
        seen: list[T] = []
        for value in values:
            if value is None or value in seen:
                continue
            seen.append(value)
        return seen
