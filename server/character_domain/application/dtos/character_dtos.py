"""Application-layer DTOs for the character domain."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .anubis_dtos import HPLogEntry, HPSummaryResponse, WeeklyConsistencyResponse


# ── Character ──────────────────────────────────────────────────────────

class CreateCharacterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)


class CharacterStatusResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    hp: int
    health_state: str
    rank: str
    aura_color: str
    current_streak: int
    longest_streak: int
    total_study_minutes: int
    life_shields: int
    rituals_used: int
    ghosting_days: int
    has_flow_state_buff: bool
    is_permanently_dead: bool
    weekly_consistency_multiplier: float
    consecutive_below_average_days: int
    created_at: datetime
    updated_at: datetime


# ── Covenant ───────────────────────────────────────────────────────────

class SetCovenantRequest(BaseModel):
    subject_type: str = Field(..., description="study_session | reading | practice_revision")
    goal_minutes: int = Field(..., gt=0)
    sign: bool = True


class CovenantResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    covenant_date: date
    subject_type: str
    goal_minutes: int
    actual_minutes: int
    status: str
    is_signed: bool
    hp_gain_multiplier: float
    goal_acceptance_label: Optional[str] = None
    goal_acceptance_message: Optional[str] = None
    is_in_penance: bool = False


# ── Study Session ──────────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    covenant_id: uuid.UUID


class CompleteSessionRequest(BaseModel):
    session_id: uuid.UUID
    duration_minutes: int = Field(..., gt=0)
    bonus_task_completed: bool = False
    reflection_completed: bool = False


class SessionCheckInRequest(BaseModel):
    session_id: uuid.UUID
    passed: bool


class SessionResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    covenant_id: uuid.UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: int
    status: str
    is_verified: bool
    hp_earned: int = 0
    old_hp: int = 0
    new_hp: int = 0
    hp_changes: list[str] = Field(default_factory=list)
    grants_flow_state: bool = False
    penance_progress_updated: bool = False


# ── Goal Validation ────────────────────────────────────────────────────

class ValidateGoalRequest(BaseModel):
    subject_type: str
    goal_minutes: int = Field(..., gt=0)


class GoalValidationResponse(BaseModel):
    accepted: bool
    label: str
    hp_gain_multiplier: float
    message: str
    suggested_cap_minutes: int
    hard_ceiling_minutes: int





# ── PVR & Session Cap ──────────────────────────────────────────────────




class PvrResponse(BaseModel):
    average_daily_minutes_7d: float
    longest_session_ever: int
    current_streak_health: str
    suggested_cap_minutes: int
    hard_ceiling_minutes: int


class CharacterAnalyticsResponse(BaseModel):
    pvr: PvrResponse
    timeline: list[HPLogEntry]
    consistency: WeeklyConsistencyResponse
    hp_summary: HPSummaryResponse
