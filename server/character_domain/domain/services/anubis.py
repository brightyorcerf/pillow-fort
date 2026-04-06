"""
Anubis — The Single Authority Over All HP Changes.

Named after the Egyptian god who weighs the heart, Anubis is a domain
service (not an entity) that centralises every HP mutation in the system.

No other component may directly modify Character.hp. All HP changes
flow through Anubis, which:
  1. Calculates the HP delta based on PRD rules
  2. Applies shields / multipliers / caps
  3. Persists an immutable HPLog audit record
  4. Fires domain events
  5. Triggers notifications at threshold crossings

Design principles:
  - Single Responsibility: Anubis owns HP. Period.
  - Open/Closed: new HP change reasons are added via HPChangeReason enum
    without modifying existing methods.
  - Dependency Inversion: depends on repository/notification interfaces,
    not concrete implementations.

PRD references: §3.1.1–§3.1.5, §3.2, §4.2
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from character_domain.domain.entities.character import Character
from character_domain.domain.entities.hp_log import HPLog
from character_domain.domain.exceptions import (
    CharacterAlreadyDeadException,
    CharacterNotFoundException,
    CharacterNotDeadException,
    MaxRitualsExhaustedException,
    RitualRequiredException,
)
from character_domain.domain.interfaces.hp_log_repository import IHPLogRepository
from character_domain.domain.interfaces.notification_service import (
    INotificationService,
    NotificationType,
)
from character_domain.domain.value_objects.ghosting_level import GhostingLevel, GhostingTier
from character_domain.domain.value_objects.goal_acceptance import (
    GoalAcceptanceLabel,
    GoalAcceptanceResult,
)
from character_domain.domain.value_objects.health_state import HealthState
from character_domain.domain.value_objects.hp_change_result import (
    ConsistencyLevel,
    DeathCause,
    GhostingPenaltyResult,
    GoalValidationResult,
    HPChangeReason,
    HPChangeResult,
    TrendEvaluationResult,
    TrendStatus,
    WeeklyConsistencyResult,
)
from character_domain.domain.value_objects.hp_event import HpEventType, HpRecoveryEvent
from character_domain.domain.value_objects.prospect_hp import (
    ProspectHPResult,
    compute_prospect_hp,
)
from character_domain.domain.value_objects.session_cap import SessionCap
from character_domain.domain.value_objects.subject_type import SubjectType


class Anubis:
    """
    Domain service — the sole arbiter of HP.

    Injected dependencies (ports):
      - hp_log_repo: persists the immutable audit trail
      - notification_service: fires push/in-app notifications
    """

    # ── PRD constants ────────────────────────────────────────────────
    MAX_HP = 100
    VITALITY_DECAY_K = 33.0          # Severity constant for decay formula
    FLOW_STATE_THRESHOLD_MIN = 90    # Minutes for flow state buff
    LIFE_SHIELD_STREAK_DAYS = 14     # Streak interval for earning shields
    TREND_SOFT_WARNING_DAYS = 2      # 2 consecutive below-avg → soft warning
    TREND_SUGGEST_BREAK_DAYS = 3     # 3 consecutive → suggest break
    WEEKLY_EVAL_DAYS = 7

    # Consistency multiplier thresholds (days of goal met out of 7)
    _CONSISTENCY_MAP: list[tuple[int, ConsistencyLevel, float]] = [
        (7, ConsistencyLevel.EXCEPTIONAL, 1.5),
        (5, ConsistencyLevel.BASELINE, 1.0),
        (3, ConsistencyLevel.STRUGGLING, 0.5),
        (0, ConsistencyLevel.CRITICAL, 0.1),
    ]

    def __init__(
        self,
        hp_log_repo: IHPLogRepository,
        notification_service: INotificationService,
    ) -> None:
        self._hp_log_repo = hp_log_repo
        self._notification_service = notification_service

    # ═════════════════════════════════════════════════════════════════
    #  1. CORE HP MUTATION — the single entry point for all HP changes
    # ═════════════════════════════════════════════════════════════════

    async def change_hp(
        self,
        character: Character,
        delta: int,
        reason: HPChangeReason,
        description: str,
    ) -> HPChangeResult:
        """
        The atomic HP mutation. Every other method in Anubis ultimately
        calls this. Handles clamping, shield checks, death detection,
        audit logging, and notifications.
        """
        old_hp = character.hp
        shield_used = False

        # Dead characters cannot gain HP without revival
        if character.is_dead and delta > 0 and reason != HPChangeReason.REVIVAL:
            raise CharacterAlreadyDeadException(
                "Cannot recover HP while dead. Revive the character first."
            )

        # Permanently dead characters cannot change HP at all
        if character.is_permanently_dead:
            raise CharacterAlreadyDeadException("Character is permanently dead.")

        # Shield auto-activation: if damage would kill, try shield first
        if delta < 0 and (old_hp + delta) <= 0 and character.life_shields > 0:
            character.use_life_shield()
            shield_used = True
            delta = 0  # Shield absorbs the killing blow
            description = f"[SHIELD] {description}"
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.LIFE_SHIELD_USED,
                title="Life Shield Activated!",
                body="Your shield absorbed a fatal blow. Stay focused!",
                data={"character_id": str(character.id)},
            )

        # Apply the delta with clamping
        new_hp = max(0, min(self.MAX_HP, old_hp + delta))
        actual_delta = new_hp - old_hp

        # Mutate the character's internal HP (via the entity's methods)
        if actual_delta < 0:
            # Use raw internal mutation since we've already done all logic
            character._hp = new_hp
            character._touch()
        elif actual_delta > 0:
            character._hp = new_hp
            character._touch()

        # Detect death
        triggered_death = new_hp <= 0 and old_hp > 0
        if triggered_death:
            character.break_streak()

        # Persist audit log
        log = HPLog.create(
            character_id=character.id,
            old_hp=old_hp,
            new_hp=new_hp,
            reason=reason,
            description=description,
            shield_used=shield_used,
            triggered_death=triggered_death,
        )
        await self._hp_log_repo.create(log)

        # Threshold notifications
        await self._check_thresholds(character, old_hp, new_hp, triggered_death)

        return HPChangeResult(
            character_id=character.id,
            old_hp=old_hp,
            new_hp=new_hp,
            delta=actual_delta,
            reason=reason,
            description=description,
            shield_used=shield_used,
            triggered_death=triggered_death,
        )

    # ═════════════════════════════════════════════════════════════════
    #  2. SESSION COMPLETION HP
    # ═════════════════════════════════════════════════════════════════

    async def apply_session_hp(
        self,
        character: Character,
        actual_minutes: int,
        goal_minutes: int,
        pvr_baseline_minutes: float,
        bonus_task_completed: bool = False,
        reflection_completed: bool = False,
    ) -> HPChangeResult:
        """
        Calculate and apply HP from a study session using the
        Prospect Theory equation (PRD §3.1.5).

        The equation uses a +5 HP y-axis shift so that perfectly
        meeting the goal earns +5 HP.
        """
        if character.is_in_penance:
            # During penance, HP does not increase. It's a test of dedication.
            effective_hp = 0
            reason = HPChangeReason.SESSION_COMPLETED
            description = (
                f"Studied {actual_minutes}/{goal_minutes} min while in penance. "
                "No HP gained, but dedication proven."
            )
        else:
            # Compute via Prospect Theory equation
            prospect = compute_prospect_hp(
                actual_minutes=actual_minutes,
                goal_minutes=goal_minutes,
                pvr_baseline_minutes=pvr_baseline_minutes,
            )

            effective_hp = prospect.final_delta

            # Apply weekly consistency multiplier
            if effective_hp > 0:
                effective_hp = int(effective_hp * character.weekly_consistency_multiplier)
                effective_hp = max(1, effective_hp)

            # Apply flat bonus HP
            if bonus_task_completed:
                effective_hp += 5
            if reflection_completed:
                effective_hp += 3

            # Determine reason
            if prospect.goal_met:
                reason = HPChangeReason.PROSPECT_GAIN
            else:
                reason = HPChangeReason.PROSPECT_LOSS

            description = prospect.description

        # Flow state check
        if actual_minutes >= self.FLOW_STATE_THRESHOLD_MIN:
            character.activate_flow_state()
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.FLOW_STATE_ACHIEVED,
                title="Flow State Achieved!",
                body=f"Incredible {actual_minutes}-minute deep work session!",
                data={"character_id": str(character.id)},
            )

        return await self.change_hp(character, effective_hp, reason, description)

    # ═════════════════════════════════════════════════════════════════
    #  3. VITALITY DECAY
    # ═════════════════════════════════════════════════════════════════

    async def apply_vitality_decay(
        self,
        character: Character,
        goal_target_minutes: int,
        actual_minutes: int,
        pvr_baseline_minutes: float,
    ) -> Optional[HPChangeResult]:
        """
        Apply HP change for goal evaluation using the Prospect Theory
        equation. Called at end-of-day by the cron.

        Returns None if character is dead or goal_target is invalid.
        """
        if character.is_dead or goal_target_minutes <= 0:
            return None

        prospect = compute_prospect_hp(
            actual_minutes=actual_minutes,
            goal_minutes=goal_target_minutes,
            pvr_baseline_minutes=pvr_baseline_minutes,
        )

        # If goal was met, no decay applies
        if prospect.goal_met:
            return None

        reason = HPChangeReason.PROSPECT_LOSS
        return await self.change_hp(
            character, prospect.final_delta, reason, prospect.description,
        )

    # ═════════════════════════════════════════════════════════════════
    #  4. GHOSTING PENALTY
    # ═════════════════════════════════════════════════════════════════

    async def apply_ghosting_penalty(
        self, character: Character, consecutive_days: int
    ) -> GhostingPenaltyResult:
        """
        PRD §3.1.3 ghosting escalation table.
        Called by the daily cron for characters that didn't sign a covenant.
        """
        hp_before = character.hp
        ghosting = GhostingLevel(consecutive_days)
        character._ghosting_days = consecutive_days

        # Permanent death at 30+ days
        if ghosting.is_permanently_dead:
            character._hp = 0
            character._is_permanently_dead = True
            character._current_streak = 0
            character._touch()

            await self._hp_log_repo.create(HPLog.create(
                character_id=character.id,
                old_hp=hp_before,
                new_hp=0,
                reason=HPChangeReason.PERMANENT_DEATH,
                description=f"Ghosted for {consecutive_days} days — permanent death.",
                triggered_death=True,
            ))

            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.PERMANENT_DEATH,
                title="Permanent Death",
                body="Your character has permanently fallen. Start a new journey.",
                data={"character_id": str(character.id)},
            )

            return GhostingPenaltyResult(
                character_id=character.id,
                ghosting_days=consecutive_days,
                tier=GhostingTier.PERMANENT_DEATH.value,
                hp_before=hp_before,
                hp_after=0,
                is_dead=True,
                is_permanently_dead=True,
                requires_feather=False,
                message="Permanent death — 30+ days ghosting.",
            )

        # HP override tiers (5-6 days → 1 HP, 7+ days → 0 HP)
        override_hp = ghosting.compute_hp_override()
        if override_hp is not None:
            await self.change_hp(
                character,
                override_hp - character.hp,
                HPChangeReason.GHOSTING_OVERRIDE,
                f"Ghosting {consecutive_days} days — HP forced to {override_hp}.",
            )

            message = (
                "HP locked at 0. Use a Phoenix Feather to recover."
                if override_hp == 0
                else f"HP dropped to {override_hp}. Return before it's too late."
            )

            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.GHOSTING_ESCALATION,
                title="Ghosting Escalation",
                body=message,
                data={"character_id": str(character.id), "days": consecutive_days},
            )

            return GhostingPenaltyResult(
                character_id=character.id,
                ghosting_days=consecutive_days,
                tier=ghosting.tier.value,
                hp_before=hp_before,
                hp_after=character.hp,
                is_dead=character.is_dead,
                is_permanently_dead=False,
                requires_feather=ghosting.requires_feather,
                message=message,
            )

        # Standard ghosting damage (−66 base + extras)
        base_damage = -66
        extra = ghosting.compute_extra_damage()
        total_damage = base_damage - extra

        result = await self.change_hp(
            character,
            total_damage,
            HPChangeReason.GHOSTING,
            f"Ghosting day {consecutive_days}: {total_damage} HP "
            f"(base −66, extra −{extra}).",
        )

        return GhostingPenaltyResult(
            character_id=character.id,
            ghosting_days=consecutive_days,
            tier=ghosting.tier.value,
            hp_before=hp_before,
            hp_after=character.hp,
            is_dead=character.is_dead,
            is_permanently_dead=False,
            requires_ritual=False,
            message=f"Ghosting penalty: {total_damage} HP.",
        )

    # ═════════════════════════════════════════════════════════════════
    #  5. MISSED DAILY GOAL
    # ═════════════════════════════════════════════════════════════════

    async def apply_missed_goal_penalty(
        self, character: Character, consecutive_misses: int = 1
    ) -> HPChangeResult:
        """
        PRD §3.1.3: Missed daily goal = −33 HP.
        Consecutive misses add extra penalties.
        """
        base = -33

        if consecutive_misses == 2:
            extra = -10
            reason = HPChangeReason.CONSECUTIVE_MISS
            desc = "Missed goal 2 days in a row — extra −10 HP."
        elif consecutive_misses >= 3:
            extra = -15
            reason = HPChangeReason.CONSECUTIVE_MISS
            desc = f"Missed goal {consecutive_misses} days in a row — extra −15 HP."
        else:
            extra = 0
            reason = HPChangeReason.MISSED_DAILY_GOAL
            desc = "Missed daily goal — −33 HP."

        total = base + extra
        return await self.change_hp(character, total, reason, desc)

    # ═════════════════════════════════════════════════════════════════
    #  6. GOAL VALIDATION (PVR-based)
    # ═════════════════════════════════════════════════════════════════

    def validate_goal(
        self,
        goal_minutes: int,
        subject_type: SubjectType,
        average_goal_minutes: float,
        average_actual_minutes: float,
        longest_session_minutes: int,
    ) -> GoalValidationResult:
        """
        Pure function — no side effects. Validates a proposed goal
        against PVR (Personal Viable Range) rules.

        Returns GoalValidationResult with acceptance label, multiplier,
        suggested cap, and hard ceiling.
        """
        minimum = subject_type.minimum_goal_minutes
        cap = SessionCap.from_average(average_actual_minutes)

        # Check minimum
        if goal_minutes < minimum:
            return GoalValidationResult(
                accepted=False,
                label=GoalAcceptanceLabel.INVALID.value,
                hp_gain_multiplier=0.0,
                message=f"Too short. Minimum is {minimum} minutes for {subject_type.value}.",
                suggested_cap_minutes=cap.suggested_cap_minutes,
                hard_ceiling_minutes=cap.hard_ceiling_minutes,
            )

        # Check ceiling
        if goal_minutes > cap.hard_ceiling_minutes:
            return GoalValidationResult(
                accepted=False,
                label=GoalAcceptanceLabel.INVALID.value,
                hp_gain_multiplier=0.0,
                message=(
                    f"Exceeds the {cap.hard_ceiling_minutes // 60}-hour hard ceiling. "
                    "Cognitive fatigue risk."
                ),
                suggested_cap_minutes=cap.suggested_cap_minutes,
                hard_ceiling_minutes=cap.hard_ceiling_minutes,
            )

        # Evaluate against average
        acceptance = GoalAcceptanceResult.evaluate(
            goal_minutes=goal_minutes,
            average_minutes=average_goal_minutes,
            minimum_minutes=minimum,
        )

        return GoalValidationResult(
            accepted=acceptance.accepted,
            label=acceptance.label.value,
            hp_gain_multiplier=acceptance.hp_gain_multiplier,
            message=acceptance.message,
            suggested_cap_minutes=cap.suggested_cap_minutes,
            hard_ceiling_minutes=cap.hard_ceiling_minutes,
        )

    # ═════════════════════════════════════════════════════════════════
    #  7. COMPUTE PVR (Personal Viable Range)
    # ═════════════════════════════════════════════════════════════════

    def compute_pvr(
        self,
        average_daily_minutes_7d: float,
        longest_session_ever: int,
        current_streak_health: str,
        average_actual_minutes_14d: float,
    ) -> dict:
        """
        Compute PVR — the personalised range of viable daily goals.

        Returns a dict matching PvrResponse fields.
        """
        cap = SessionCap.from_average(average_actual_minutes_14d)

        return {
            "average_daily_minutes_7d": round(average_daily_minutes_7d, 1),
            "longest_session_ever": longest_session_ever,
            "current_streak_health": current_streak_health,
            "suggested_cap_minutes": cap.suggested_cap_minutes,
            "hard_ceiling_minutes": cap.hard_ceiling_minutes,
        }

    # ═════════════════════════════════════════════════════════════════
    #  8. EVALUATE DOWNWARD TREND
    # ═════════════════════════════════════════════════════════════════

    async def evaluate_trend(
        self, character: Character, consecutive_below_days: int
    ) -> TrendEvaluationResult:
        """
        PRD §3.1.5: Evaluate downward trend — advisory only, no HP penalties.

        2 consecutive days below average → soft warning
        3+ consecutive days → suggest break
        """
        if consecutive_below_days < self.TREND_SOFT_WARNING_DAYS:
            character.reset_below_average_trend()
            return TrendEvaluationResult(
                status=TrendStatus.NONE,
                consecutive_below_days=consecutive_below_days,
                hp_penalty=0,
                message="On track.",
            )

        if consecutive_below_days >= self.TREND_SUGGEST_BREAK_DAYS:
            trend_status = TrendStatus.ESCALATED
            msg = (
                "Suggested to take a break and try again tomorrow or "
                "after sometime. It's ok to have bad days sometimes."
            )
        else:
            trend_status = TrendStatus.WARNING
            msg = (
                "Your goals have been trending lower. "
                "Just checking in!"
            )

        # Advisory only — no HP penalty applied
        character._consecutive_below_average_days = consecutive_below_days
        character._touch()

        # Notification
        await self._notification_service.send(
            user_id=character.user_id,
            notification_type=NotificationType.TREND_WARNING,
            title="Downward Trend Detected",
            body=msg,
            data={
                "character_id": str(character.id),
                "consecutive_days": consecutive_below_days,
            },
        )

        return TrendEvaluationResult(
            status=trend_status,
            consecutive_below_days=consecutive_below_days,
            hp_penalty=0,
            message=msg,
        )

    # ═════════════════════════════════════════════════════════════════
    #  9. TREND RECOVERY BONUS
    # ═════════════════════════════════════════════════════════════════

    async def apply_trend_recovery(
        self, character: Character, consecutive_at_average_days: int = 1
    ) -> Optional[HPChangeResult]:
        """
        PRD §3.1.5 Trend Recovery:
          1 day back at average → trend warning cleared
          2 consecutive days at average → +5 HP recovery bonus
          3+ consecutive days at or above average → trend fully reset
        """
        if character.consecutive_below_average_days < self.TREND_SOFT_WARNING_DAYS:
            # No trend was active — nothing to recover from
            character.reset_below_average_trend()
            return None

        character.reset_below_average_trend()

        if consecutive_at_average_days >= 2:
            return await self.change_hp(
                character,
                5,
                HPChangeReason.TREND_RECOVERY,
                "Trend recovered! +5 HP bonus for getting back on track.",
            )

        return None

    # ═════════════════════════════════════════════════════════════════
    #  10. WEEKLY CONSISTENCY EVALUATION
    # ═════════════════════════════════════════════════════════════════

    async def compute_weekly_consistency(
        self,
        character: Character,
        days_goal_met: int,
        days_total: int = 7,
    ) -> WeeklyConsistencyResult:
        """
        PRD §3.1.4: Evaluate weekly consistency and set the multiplier.

        7/7 days met  → 1.5x  (Exceptional)
        5-6/7         → 1.0x  (Baseline)
        3-4/7         → 0.5x  (Struggling)
        0-2/7         → 0.1x  (Critical)
        """
        level = ConsistencyLevel.CRITICAL
        multiplier = 0.1

        for threshold, lvl, mult in self._CONSISTENCY_MAP:
            if days_goal_met >= threshold:
                level = lvl
                multiplier = mult
                break

        character.set_weekly_consistency_multiplier(multiplier)

        messages = {
            ConsistencyLevel.EXCEPTIONAL: (
                f"Perfect week! {days_goal_met}/{days_total} goals hit. "
                "HP gains boosted to 1.5×!"
            ),
            ConsistencyLevel.BASELINE: (
                f"Solid week: {days_goal_met}/{days_total} goals hit. "
                "HP gains at standard rate."
            ),
            ConsistencyLevel.STRUGGLING: (
                f"Rough week: {days_goal_met}/{days_total} goals. "
                "HP gains reduced to 0.5× — you can bounce back!"
            ),
            ConsistencyLevel.CRITICAL: (
                f"Critical: only {days_goal_met}/{days_total} goals met. "
                "HP gains at 0.1× — every session counts."
            ),
        }

        msg = messages[level]

        # Weekly report notification
        await self._notification_service.send(
            user_id=character.user_id,
            notification_type=NotificationType.WEEKLY_REPORT,
            title="Weekly Consistency Report",
            body=msg,
            data={
                "character_id": str(character.id),
                "level": level.value,
                "multiplier": multiplier,
            },
        )

        return WeeklyConsistencyResult(
            level=level,
            multiplier=multiplier,
            days_hit=days_goal_met,
            days_total=days_total,
            message=msg,
        )

    # ═════════════════════════════════════════════════════════════════
    #  11. STREAK MANAGEMENT (delegated through Anubis)
    # ═════════════════════════════════════════════════════════════════

    async def process_streak_extension(
        self, character: Character
    ) -> Optional[HPChangeResult]:
        """
        Extend the streak and apply any milestone HP bonuses.
        Streak bonuses flow through change_hp for audit.
        """
        old_streak = character.current_streak
        old_rank = character.rank

        character.extend_streak()
        new_streak = character.current_streak

        result = None

        # Streak milestone HP bonuses
        if new_streak == 3:
            result = await self.change_hp(
                character, 10, HPChangeReason.STREAK_3_BONUS,
                "3-day streak bonus! +10 HP.",
            )
        elif new_streak == 7:
            result = await self.change_hp(
                character, 20, HPChangeReason.STREAK_7_BONUS,
                "7-day streak bonus! +20 HP.",
            )

        # Life shield notification
        if new_streak % self.LIFE_SHIELD_STREAK_DAYS == 0:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.LIFE_SHIELD_EARNED,
                title="Life Shield Earned!",
                body=f"{new_streak}-day streak! You've earned a Life Shield.",
                data={"character_id": str(character.id)},
            )

        # Rank change notification
        new_rank = character.rank
        if new_rank != old_rank:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.RANK_UP,
                title=f"Rank Up: {new_rank.value}!",
                body=f"Congratulations! You've ascended from {old_rank.value} to {new_rank.value}.",
                data={
                    "character_id": str(character.id),
                    "old_rank": old_rank.value,
                    "new_rank": new_rank.value,
                },
            )

        # Streak milestone notification
        if new_streak in (3, 7, 14, 30, 90, 180, 365):
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.STREAK_MILESTONE,
                title=f"{new_streak}-Day Streak!",
                body=f"Incredible discipline — {new_streak} consecutive days!",
                data={"character_id": str(character.id), "streak": new_streak},
            )

        return result

    # ═════════════════════════════════════════════════════════════════
    #  12. REVIVAL (ritual / phoenix feather)
    # ═════════════════════════════════════════════════════════════════

    async def revive_with_phoenix_feather(
        self, character: Character
    ) -> HPChangeResult:
        """Revive via Phoenix Feather — the sole revival path."""
        if not character.is_dead:
            raise CharacterNotDeadException()

        character._ghosting_days = 0
        character._touch()

        return await self.change_hp(
            character, 50, HPChangeReason.REVIVAL,
            "Revived via Phoenix Feather! Welcome back!",
        )

    # ═════════════════════════════════════════════════════════════════
    #  13. BONUS TASK / REFLECTION HP
    # ═════════════════════════════════════════════════════════════════

    async def apply_bonus_task_hp(
        self, character: Character
    ) -> HPChangeResult:
        """Bonus task completed — +5 HP."""
        return await self.change_hp(
            character, 5, HPChangeReason.BONUS_TASK,
            "Bonus task completed! +5 HP.",
        )

    async def apply_reflection_hp(
        self, character: Character
    ) -> HPChangeResult:
        """Reflection logged — +3 HP."""
        return await self.change_hp(
            character, 3, HPChangeReason.REFLECTION_LOGGED,
            "Reflection logged. +3 HP.",
        )

    # ═════════════════════════════════════════════════════════════════
    #  15. GET HP TIMELINE
    # ═════════════════════════════════════════════════════════════════

    async def get_hp_timeline(
        self, character_id: uuid.UUID, limit: int = 50
    ) -> list[HPLog]:
        """Retrieve the HP audit trail for a character."""
        return await self._hp_log_repo.get_by_character(character_id, limit)

    async def get_hp_summary_today(
        self, character_id: uuid.UUID
    ) -> dict:
        """Get today's HP change summary."""
        logs = await self._hp_log_repo.get_today(character_id)
        total_delta = await self._hp_log_repo.get_total_delta_today(character_id)

        return {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "total_changes": len(logs),
            "net_delta": total_delta,
            "events": [
                {
                    "reason": log.reason.value,
                    "delta": log.delta,
                    "description": log.description,
                    "timestamp": log.created_at.isoformat(),
                }
                for log in logs
            ],
        }

    # ═════════════════════════════════════════════════════════════════
    #  16. PROCESS DAILY EVALUATION (orchestrator for cron)
    # ═════════════════════════════════════════════════════════════════

    async def process_daily_evaluation(
        self,
        character: Character,
        covenant_goal_minutes: Optional[int],
        covenant_actual_minutes: Optional[int],
        consecutive_ghosting_days: int,
        consecutive_below_average_days: int,
        average_daily_minutes: float,
    ) -> dict:
        """
        The master daily evaluation — called by the cron use case.
        Orchestrates all end-of-day HP logic in the correct order.

        Returns a summary dict for logging/debugging.
        """
        results = {}

        # 1. Ghosting check (no covenant signed today)
        if covenant_goal_minutes is None:
            ghosting_result = await self.apply_ghosting_penalty(
                character, consecutive_ghosting_days
            )
            results["ghosting"] = ghosting_result
            character.break_streak()
            return results

        # 2. Goal evaluation
        goal_met = (
            covenant_actual_minutes is not None
            and covenant_actual_minutes >= covenant_goal_minutes
        )

        if goal_met:
            # Extend streak
            streak_result = await self.process_streak_extension(character)
            results["streak"] = streak_result

            # Trend recovery
            if consecutive_below_average_days >= self.TREND_SOFT_WARNING_DAYS:
                trend_recovery = await self.apply_trend_recovery(character)
                results["trend_recovery"] = trend_recovery
        else:
            # Apply vitality decay using Prospect Theory equation
            if covenant_actual_minutes and covenant_actual_minutes > 0:
                decay_result = await self.apply_vitality_decay(
                    character, covenant_goal_minutes, covenant_actual_minutes,
                    pvr_baseline_minutes=average_daily_minutes,
                )
                results["vitality_decay"] = decay_result
            else:
                # Complete miss
                miss_result = await self.apply_missed_goal_penalty(character)
                results["missed_goal"] = miss_result

            character.break_streak()

            # Evaluate downward trend
            if (
                covenant_actual_minutes is not None
                and average_daily_minutes > 0
                and covenant_actual_minutes < average_daily_minutes
            ):
                trend_result = await self.evaluate_trend(
                    character, consecutive_below_average_days + 1
                )
                results["trend"] = trend_result

        return results

    # ═════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS
    # ═════════════════════════════════════════════════════════════════

    # (old _compute_session_hp lookup table removed — replaced by prospect_hp.py)

    async def _check_thresholds(
        self,
        character: Character,
        old_hp: int,
        new_hp: int,
        triggered_death: bool,
    ) -> None:
        """Fire notifications when HP crosses critical thresholds."""
        if triggered_death:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.DEATH,
                title="Character Died",
                body="Your character has fallen. Use a Phoenix Feather to revive.",
                data={"character_id": str(character.id)},
            )
            return

        # Crossed below critical (33)
        if old_hp > 33 >= new_hp:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.HP_CRITICAL,
                title="HP Critical!",
                body=f"HP is at {new_hp}. One more miss could be fatal.",
                data={"character_id": str(character.id), "hp": new_hp},
            )
        # Crossed below warning (66 → damaged)
        elif old_hp > 66 >= new_hp:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.HP_LOW_WARNING,
                title="HP Dropping",
                body=f"HP is at {new_hp}. Stay consistent to recover.",
                data={"character_id": str(character.id), "hp": new_hp},
            )
