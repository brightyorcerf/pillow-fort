"""
Character aggregate root — the digital "Mini-Me" companion.

Encapsulates the entire HP system, state machine, streak tracking,
ghosting penalties, and rank progression from the PRD.

The character's state is calculated server-side (PRD §4.2)
to prevent client-side manipulation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.events import (
    CharacterCreated,
    CharacterDied,
    CharacterRevived,
    DomainEvent,
    HpChanged,
    RankChanged,
    StreakMilestone,
)
from character_domain.domain.exceptions import (
    CharacterAlreadyDeadException,
    CharacterNotDeadException,
)
from character_domain.domain.value_objects.ghosting_level import GhostingLevel, GhostingTier
from character_domain.domain.value_objects.health_state import HealthState
from character_domain.domain.value_objects.hp_event import HpDamageEvent, HpRecoveryEvent
from character_domain.domain.value_objects.hp_event import HpEventType
from character_domain.domain.value_objects.rank import Rank
# Phoenix Feather revival HP
FEATHER_REVIVE_HP = 50


class Character:
    """
    Aggregate root for the character bounded context.

    Invariants:
      - HP is always in [0, 100]
      - State is derived from HP (no separate storage)
      - Dead characters cannot gain HP without revival
      - Ghosting >= 7 days locks HP at 0 until Phoenix Feather revival
      - 30+ ghosting days = permanent death
    """

    MAX_HP = 100
    LIFE_SHIELD_STREAK_INTERVAL = 14  # PRD: earned every 14-day streak

    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        hp: int = 100,
        current_streak: int = 0,
        longest_streak: int = 0,
        total_study_minutes: int = 0,
        life_shields: int = 0,
        rituals_used: int = 0,
        ghosting_days: int = 0,
        has_flow_state_buff: bool = False,
        is_permanently_dead: bool = False,
        is_in_penance: bool = False,
        weekly_consistency_multiplier: float = 1.0,
        consecutive_below_average_days: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = id
        self._user_id = user_id
        self._name = name
        self._hp = max(0, min(hp, self.MAX_HP))
        self._current_streak = current_streak
        self._longest_streak = longest_streak
        self._total_study_minutes = total_study_minutes
        self._life_shields = life_shields
        self._rituals_used = rituals_used
        self._ghosting_days = ghosting_days
        self._has_flow_state_buff = has_flow_state_buff
        self._is_permanently_dead = is_permanently_dead
        self._is_in_penance = is_in_penance
        self._weekly_consistency_multiplier = weekly_consistency_multiplier
        self._consecutive_below_average_days = consecutive_below_average_days
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)
        self._domain_events: list[DomainEvent] = []

    # ── Factory ────────────────────────────────────────────────────────

    @classmethod
    def create(cls, user_id: uuid.UUID, name: str) -> Character:
        char = cls(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            hp=100,
        )
        char._record_event(CharacterCreated(character_id=char.id, user_id=user_id))
        return char

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def health_state(self) -> HealthState:
        return HealthState.from_hp(self._hp)

    @property
    def is_dead(self) -> bool:
        return self._hp <= 0

    @property
    def is_permanently_dead(self) -> bool:
        return self._is_permanently_dead

    @property
    def is_in_penance(self) -> bool:
        return self._is_in_penance

    @property
    def current_streak(self) -> int:
        return self._current_streak

    @property
    def longest_streak(self) -> int:
        return self._longest_streak

    @property
    def total_study_minutes(self) -> int:
        return self._total_study_minutes

    @property
    def life_shields(self) -> int:
        return self._life_shields

    @property
    def rituals_used(self) -> int:
        return self._rituals_used

    @property
    def ghosting_days(self) -> int:
        return self._ghosting_days

    @property
    def has_flow_state_buff(self) -> bool:
        return self._has_flow_state_buff

    @property
    def rank(self) -> Rank:
        return Rank.from_streak(self._current_streak)

    @property
    def weekly_consistency_multiplier(self) -> float:
        return self._weekly_consistency_multiplier

    @property
    def consecutive_below_average_days(self) -> int:
        return self._consecutive_below_average_days

    @property
    def ghosting_level(self) -> GhostingLevel:
        return GhostingLevel(self._ghosting_days)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def domain_events(self) -> list[DomainEvent]:
        return list(self._domain_events)

    # ── HP Mutation (core state machine) ───────────────────────────────

    def apply_damage(self, event: HpDamageEvent) -> None:
        """Apply an HP damage event. Respects death, shields, and ghosting."""
        if self._is_permanently_dead:
            raise CharacterAlreadyDeadException("Character is permanently dead.")

        old_hp = self._hp
        self._hp = max(0, self._hp + event.hp_change)  # hp_change is negative
        self._touch()

        self._record_event(HpChanged(
            character_id=self.id,
            old_hp=old_hp,
            new_hp=self._hp,
            event_type=event.event_type.value,
            reason=event.reason,
        ))

        if self._hp <= 0 and old_hp > 0:
            self._on_death()

    def apply_recovery(self, event: HpRecoveryEvent) -> None:
        """Apply an HP recovery event. Capped at 100. Dead chars cannot recover."""
        if self.is_dead:
            raise CharacterAlreadyDeadException(
                "Cannot recover HP while dead. Revive the character first."
            )

        old_hp = self._hp
        # Apply weekly consistency multiplier (PRD §3.1.4)
        effective_gain = int(event.hp_change * self._weekly_consistency_multiplier)
        self._hp = min(self.MAX_HP, self._hp + effective_gain)
        self._touch()

        self._record_event(HpChanged(
            character_id=self.id,
            old_hp=old_hp,
            new_hp=self._hp,
            event_type=event.event_type.value,
            reason=event.reason,
        ))

    def apply_ghosting(self, consecutive_days: int) -> None:
        """
        Process ghosting penalties — PRD §3.1.3 escalation table.
        Called by the daily cron job.
        """
        if self._is_permanently_dead:
            return

        self._ghosting_days = consecutive_days
        ghosting = self.ghosting_level

        if ghosting.is_permanently_dead:
            self._permanent_death()
            return

        override_hp = ghosting.compute_hp_override()
        if override_hp is not None:
            old_hp = self._hp
            self._hp = override_hp
            self._touch()
            self._record_event(HpChanged(
                character_id=self.id,
                old_hp=old_hp,
                new_hp=self._hp,
                event_type="ghosting_override",
                reason=f"Ghosting for {consecutive_days} days — HP forced to {override_hp}.",
            ))
            if self._hp <= 0 and old_hp > 0:
                self._on_death()
            return

        # Standard ghosting damage + extra
        base_damage = -66
        extra = ghosting.compute_extra_damage()
        total_damage = base_damage - extra

        old_hp = self._hp
        self._hp = max(0, self._hp + total_damage)
        self._touch()

        self._record_event(HpChanged(
            character_id=self.id,
            old_hp=old_hp,
            new_hp=self._hp,
            event_type="ghosting",
            reason=f"Ghosting day {consecutive_days}: {total_damage} HP.",
        ))

        if self._hp <= 0 and old_hp > 0:
            self._on_death()

    # ── Vitality decay function (PRD §4.2 State Machine) ──────────────

    def apply_vitality_decay(
        self, goal_target_minutes: int, actual_minutes: int, severity_k: float = 33.0
    ) -> None:
        """
        PRD formula: V_new = V_old - ((G_target - G_actual) / G_target) * K
        Where V = Vitality (HP), G = Goal, K = severity constant.
        """
        if self.is_dead or goal_target_minutes <= 0:
            return

        shortfall_ratio = (goal_target_minutes - actual_minutes) / goal_target_minutes
        if shortfall_ratio <= 0:
            return  # Met or exceeded goal — no decay

        damage = int(shortfall_ratio * severity_k)
        if damage > 0:
            old_hp = self._hp
            self._hp = max(0, self._hp - damage)
            self._touch()
            self._record_event(HpChanged(
                character_id=self.id,
                old_hp=old_hp,
                new_hp=self._hp,
                event_type="vitality_decay",
                reason=f"Studied {actual_minutes}/{goal_target_minutes} min — decay of {damage} HP.",
            ))
            if self._hp <= 0 and old_hp > 0:
                self._on_death()

    # ── Streak management ──────────────────────────────────────────────

    def extend_streak(self) -> None:
        old_rank = self.rank
        self._current_streak += 1
        if self._current_streak > self._longest_streak:
            self._longest_streak = self._current_streak

        # Life Shield earned every 14-day streak (PRD §3.1.1)
        if self._current_streak % self.LIFE_SHIELD_STREAK_INTERVAL == 0:
            self._life_shields += 1

        # Streak milestone bonuses
        if self._current_streak == 3:
            self.apply_recovery(HpRecoveryEvent(
                event_type=HpEventType.STREAK_3_DAY,
                reason="3-day streak bonus!",
            ))
        elif self._current_streak == 7:
            self.apply_recovery(HpRecoveryEvent(
                event_type=HpEventType.STREAK_7_DAY,
                reason="7-day streak bonus!",
            ))

        new_rank = self.rank
        if new_rank != old_rank:
            self._record_event(RankChanged(
                character_id=self.id,
                old_rank=old_rank.value,
                new_rank=new_rank.value,
            ))

        if self._current_streak in (3, 7, 14, 30, 90, 180, 365):
            self._record_event(StreakMilestone(
                character_id=self.id,
                streak_days=self._current_streak,
            ))

        self._ghosting_days = 0
        self._touch()

    def break_streak(self) -> None:
        self._current_streak = 0
        self._touch()

    def use_life_shield(self) -> bool:
        """
        Use a Life Shield to auto-revive from an accidental miss.
        Returns True if shield was available and used.
        """
        if self._life_shields > 0:
            self._life_shields -= 1
            self._touch()
            return True
        return False

    # ── Flow State Buff (PRD §3.1.1) ──────────────────────────────────

    def activate_flow_state(self) -> None:
        """Granted when a deep work session exceeds 90 minutes."""
        self._has_flow_state_buff = True
        self._touch()

    def deactivate_flow_state(self) -> None:
        self._has_flow_state_buff = False
        self._touch()

    # ── Study tracking ─────────────────────────────────────────────────

    def add_study_minutes(self, minutes: int) -> None:
        self._total_study_minutes += minutes
        self._touch()

    # ── Weekly consistency (PRD §3.1.4) ────────────────────────────────

    def set_weekly_consistency_multiplier(self, multiplier: float) -> None:
        """Set by the weekly cron: 1.5, 1.0, 0.5, or 0.1."""
        self._weekly_consistency_multiplier = max(0.1, min(1.5, multiplier))
        self._touch()

    # ── Downward trend tracking (PRD §3.1.5) ───────────────────────────

    def record_below_average_day(self) -> None:
        self._consecutive_below_average_days += 1
        self._touch()

    def reset_below_average_trend(self) -> None:
        self._consecutive_below_average_days = 0
        self._touch()

    # ── Death & Revival ────────────────────────────────────────────────

    def _on_death(self) -> None:
        self.break_streak()
        self._record_event(CharacterDied(
            character_id=self.id,
            total_study_minutes=self._total_study_minutes,
        ))

    def _permanent_death(self) -> None:
        """PRD: 30+ ghosting days → account permanently killed."""
        self._hp = 0
        self._is_permanently_dead = True
        self._current_streak = 0
        self._touch()
        self._record_event(CharacterDied(
            character_id=self.id,
            total_study_minutes=self._total_study_minutes,
            is_permanent=True,
        ))

    def revive_with_phoenix_feather(self) -> None:
        """Revive via Phoenix Feather — the sole revival path."""
        if not self.is_dead:
            raise CharacterNotDeadException()

        self._hp = FEATHER_REVIVE_HP
        self._ghosting_days = 0
        self._touch()
        self._record_event(CharacterRevived(
            character_id=self.id,
            method="phoenix_feather",
            revived_hp=FEATHER_REVIVE_HP,
        ))

    def full_reset(self) -> None:
        """
        PRD: After 3 rituals exhausted + ghost again → full reset.
        All progress, streaks, and HP wiped.
        """
        self._hp = 100
        self._current_streak = 0
        self._longest_streak = 0
        self._total_study_minutes = 0
        self._life_shields = 0
        self._rituals_used = 0
        self._ghosting_days = 0
        self._is_permanently_dead = False
        self._is_in_penance = False
        self._weekly_consistency_multiplier = 1.0
        self._consecutive_below_average_days = 0
        self._touch()

    # ── Penance ────────────────────────────────────────────────────────

    def start_penance(self) -> None:
        self._is_in_penance = True
        self._touch()

    def clear_penance(self) -> None:
        self._is_in_penance = False
        self._touch()

    # ── Eulogy (PRD §3.2) ──────────────────────────────────────────────

    def generate_eulogy(self) -> dict:
        """The Eulogy: a generated report of all 'Promises Kept'."""
        return {
            "character_name": self._name,
            "total_study_hours": round(self._total_study_minutes / 60, 1),
            "longest_streak": self._longest_streak,
            "rank_achieved": Rank.from_streak(self._longest_streak).value,
            "life_shields_earned": self._life_shields,
            "born_at": self._created_at.isoformat(),
            "died_at": self._updated_at.isoformat(),
        }

    # ── Internal helpers ───────────────────────────────────────────────

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_events(self) -> None:
        self._domain_events.clear()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Character):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
