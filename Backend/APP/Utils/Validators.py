from __future__ import annotations

from fastapi import HTTPException, status


class Validators:
    GENDERS = {"Male", "Female", "Other"}
    BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"}
    ATTENDANCE_STATUSES = {"Present", "Absent"}
    FEE_STATUSES = {"Paid", "Pending"}
    USER_ROLES = {"Student", "Teacher", "Staff", "Admin"}
    EXAM_TYPES = {"Midterm", "Final", "Assignment", "Practical", "Other"}
    STAFF_ROLES = {
        "Administration",
        "Librarian",
        "Clerk",
        "Lab Assistant",
        "Maintenance",
        "Security",
        "Other",
    }

    @staticmethod
    def hasText(value: str | None) -> bool:
        return value is not None and value.strip() != ""

    @staticmethod
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    @staticmethod
    def requireText(value: str | None, fieldName: str) -> None:
        Validators.require(Validators.hasText(value), f"{fieldName} is required")

    @staticmethod
    def normalizeRequiredChoice(value: str | None, allowedValues: set[str], fieldName: str) -> str:
        Validators.requireText(value, fieldName)
        return Validators._normalizeChoice(value, allowedValues, fieldName)

    @staticmethod
    def normalizeOptionalChoice(value: str | None, allowedValues: set[str], fieldName: str) -> str | None:
        if not Validators.hasText(value):
            return None
        return Validators._normalizeChoice(value, allowedValues, fieldName)

    @staticmethod
    def _normalizeChoice(value: str | None, allowedValues: set[str], fieldName: str) -> str:
        assert value is not None
        trimmed = value.strip()
        for option in allowedValues:
            if option.lower() == trimmed.lower():
                return option
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{fieldName} must be one of: {', '.join(sorted(allowedValues))}",
        )
