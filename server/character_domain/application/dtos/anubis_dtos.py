"""Application-layer DTOs for the Anubis domain service endpoints."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── HP Change ─────────────────────────────────────────────────────────


class HPChangeResponse(BaseModel):
    character_id: uuid.UUID
    old_hp: int
    new_hp: int
    delta: int
    reason: str
    description: str
    shield_used: bool
    triggered_death: bool
    timestamp: datetime


# ── HP Timeline ───────────────────────────────────────────────────────


class HPLogEntry(BaseModel):
    id: uuid.UUID
    old_hp: int
    new_hp: int
    delta: int
    reason: str
    description: str
    shield_used: bool
    triggered_death: bool
    created_at: datetime


class HPTimelineResponse(BaseModel):
    character_id: uuid.UUID
    entries: list[HPLogEntry]
    total_count: int


# ── HP Summary ────────────────────────────────────────────────────────


class HPSummaryEvent(BaseModel):
    reason: str
    delta: int
    description: str
    timestamp: str


class HPSummaryResponse(BaseModel):
    date: str
    total_changes: int
    net_delta: int
    events: list[HPSummaryEvent]


# ── Goal Validation ──────────────────────────────────────────────────


class AnubisGoalValidationRequest(BaseModel):
    subject_type: str = Field(..., description="study_session | reading | practice_revision")
    goal_minutes: int = Field(..., gt=0)


class AnubisGoalValidationResponse(BaseModel):
    accepted: bool
    label: str
    hp_gain_multiplier: float
    message: str
    suggested_cap_minutes: int
    hard_ceiling_minutes: int


# ── Trend Evaluation ─────────────────────────────────────────────────


class TrendEvaluationResponse(BaseModel):
    status: str
    consecutive_below_days: int
    hp_penalty: int
    message: str


# ── Weekly Consistency ────────────────────────────────────────────────


class WeeklyConsistencyResponse(BaseModel):
    level: str
    multiplier: float
    days_hit: int
    days_total: int
    message: str


# ── Ghosting Penalty ─────────────────────────────────────────────────


class GhostingPenaltyResponse(BaseModel):
    character_id: uuid.UUID
    ghosting_days: int
    tier: str
    hp_before: int
    hp_after: int
    is_dead: bool
    is_permanently_dead: bool
    requires_feather: bool
    message: str


# ── Session HP ────────────────────────────────────────────────────────


class ApplySessionHPRequest(BaseModel):
    session_id: uuid.UUID
    duration_minutes: int = Field(..., gt=0)
    goal_minutes: int = Field(..., gt=0)
    hp_gain_multiplier: float = Field(default=1.0, ge=0.0, le=2.0)


# ── Bonus / Reflection ───────────────────────────────────────────────


class BonusTaskRequest(BaseModel):
    """No additional fields needed — just identifies the character."""
    pass


class ReflectionRequest(BaseModel):
    """No additional fields needed — just identifies the character."""
    pass


# ── Daily Evaluation (cron) ──────────────────────────────────────────


class DailyEvaluationResponse(BaseModel):
    character_id: uuid.UUID
    results: dict
    final_hp: int
    final_state: str
