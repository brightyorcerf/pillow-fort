"""Application-layer DTOs for the unified Revival endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field

from .reaper_dtos import (
    ActivePenanceInfo,
    DeathHistoryResponse,
    RevivalHistoryResponse,
    ReaperEulogyResponse,
)


class RevivalRequest(BaseModel):
    method: Literal["feather"] = Field(..., description="Revival method (feather only)")


class RevivalStatusResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    penance_eligible: Optional[bool] = None
    active_penance: Optional[ActivePenanceInfo] = None
    feather_eligible: Optional[bool] = None
    feathers_available: Optional[int] = None
    
    # Eulogies and histories included right here
    death_history: Optional[DeathHistoryResponse] = None
    revival_history: Optional[RevivalHistoryResponse] = None
    eulogies: list[ReaperEulogyResponse] = Field(default_factory=list)
