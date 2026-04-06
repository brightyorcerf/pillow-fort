"""Application-layer DTOs for the Reaper domain service endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Death Record ──────────────────────────────────────────────────────


class DeathRecordResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    cause: str
    hp_at_death: int
    total_hours_in_life: float
    consecutive_ghost_days_at_death: int
    rituals_used_at_death: int
    longest_streak_at_death: int
    eulogy_generated: bool
    is_permanent: bool
    died_at: datetime


class DeathHistoryResponse(BaseModel):
    character_id: uuid.UUID
    deaths: list[DeathRecordResponse]
    total_deaths: int


# ── Revival ───────────────────────────────────────────────────────────


class RevivalAttemptResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    death_record_id: uuid.UUID
    method: str
    hp_restored_to: int
    success: bool
    fail_reason: Optional[str] = None
    created_at: datetime


class RevivalHistoryResponse(BaseModel):
    character_id: uuid.UUID
    attempts: list[RevivalAttemptResponse]
    total_attempts: int
    successful_revivals: int


# ── Revival Options ───────────────────────────────────────────────────


class ActivePenanceInfo(BaseModel):
    id: str
    days_completed: int
    days_remaining: int
    progress_pct: float


class RevivalOptionsResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    penance_eligible: Optional[bool] = None
    active_penance: Optional[ActivePenanceInfo] = None
    feather_eligible: Optional[bool] = None
    feathers_available: Optional[int] = None
    can_restore_unfair: Optional[bool] = None


# ── Penance Streak ────────────────────────────────────────────────────


class PenanceStreakResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    attempt_number: int
    required_days: int
    days_completed: int
    days_remaining: int
    progress_pct: float
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None


class PenanceProgressRequest(BaseModel):
    goal_hit: bool


# ── Phoenix Feather ───────────────────────────────────────────────────


class FeatherReviveRequest(BaseModel):
    """No body fields needed — feather is auto-selected."""
    pass


# (ReaperRitualAdvanceRequest removed — rituals no longer exist)


# ── Eulogy ────────────────────────────────────────────────────────────


class ReaperEulogyResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    character_name: str
    total_study_hours: float
    longest_streak: int
    rank_achieved: str
    life_shields_earned: int
    rituals_completed: int
    total_covenants_signed: int
    total_covenants_kept: int
    born_at: datetime
    died_at: datetime


# ── Unfair Death ──────────────────────────────────────────────────────


class RestoreUnfairDeathRequest(BaseModel):
    death_record_id: uuid.UUID
    compensation_hp: int = Field(default=100, ge=1, le=100)
