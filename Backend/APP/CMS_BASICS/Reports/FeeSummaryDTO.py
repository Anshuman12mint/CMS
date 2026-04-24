from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from APP.CMS_BASICS.fees.FeeDTO import FeeDTO


class FeeSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    paidCount: int = 0
    pendingCount: int = 0
    paidAmount: Decimal = Decimal("0")
    pendingAmount: Decimal = Decimal("0")
    pendingFees: list[FeeDTO] = Field(default_factory=list)
