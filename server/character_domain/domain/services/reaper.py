"""
Reaper — The Single Authority Over Death and All Revival Paths.

Named after the archetypal figure of death, the Reaper is a domain
service that orchestrates:
  - Character death processing and DeathRecord creation
  - All revival paths (Phoenix Feather, Penance Streak, Re-engagement Ritual)
  - Eligibility checks for each revival method
  - Penance streak progress tracking
  - Ritual lifecycle (initiate → advance → complete/fail)
  - Unfair death restoration
  - Eulogy generation delegation

The Reaper delegates HP mutations to Anubis (the sole HP authority)
and delegates eulogy generation to the EulogyService.

Design principles:
  - Single Responsibility: Reaper owns death & revival. Period.
  - Open/Closed: new revival methods added via RevivalMethod enum.
  - Dependency Inversion: depends on repository/service interfaces.

PRD references: §3.1.3 (Ritual Progression), §3.2 (Eulogy),
                Sequence Diagrams §6 (Death & Revival Flows).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from character_domain.domain.entities.character import Character
from character_domain.domain.entities.death_record import DeathRecord
from character_domain.domain.entities.penance_streak import PenanceStreak
from character_domain.domain.entities.phoenix_feather import PhoenixFeather
from character_domain.domain.entities.revival_attempt import RevivalAttempt
from character_domain.domain.entities.ritual_progress import RitualProgress
from character_domain.domain.exceptions import (
    CharacterAlreadyDeadException,
    CharacterNotDeadException,
    CharacterNotFoundException,
    DeathRecordNotFoundException,
    NoAvailableFeatherException,
    NoPenanceActiveException,
    PenanceAlreadyActiveException,
    PermanentlyDeadException,
    RevivalNotEligibleException,
)
from character_domain.domain.interfaces.death_record_repository import IDeathRecordRepository
from character_domain.domain.interfaces.eulogy_service import IEulogyService
from character_domain.domain.interfaces.notification_service import (
    INotificationService,
    NotificationType,
)
from character_domain.domain.interfaces.penance_streak_repository import IPenanceStreakRepository
from character_domain.domain.interfaces.phoenix_feather_repository import IPhoenixFeatherRepository
from character_domain.domain.interfaces.revival_attempt_repository import IRevivalAttemptRepository
from character_domain.domain.services.anubis import Anubis
from character_domain.domain.value_objects.reaper_enums import (
    DeathCause,
    FeatherStatus,
    PenanceStatus,
    RevivalMethod,
)


class Reaper:
    """
    Domain service — the sole arbiter of death and revival.

    Injected dependencies (ports):
      - death_record_repo: persists death records
      - revival_attempt_repo: persists revival attempts
      - penance_repo: manages penance streak lifecycle
      - feather_repo: manages phoenix feather inventory
      - anubis: delegates HP mutations
      - eulogy_service: generates eulogies
      - notification_service: fires push/in-app notifications
    """

    PENANCE_REQUIRED_DAYS = 7
    REVIVE_HP = 50

    def __init__(
        self,
        death_record_repo: IDeathRecordRepository,
        revival_attempt_repo: IRevivalAttemptRepository,
        penance_repo: IPenanceStreakRepository,
        feather_repo: IPhoenixFeatherRepository,
        anubis: Anubis,
        eulogy_service: IEulogyService,
        notification_service: INotificationService,
    ) -> None:
        self._death_record_repo = death_record_repo
        self._revival_attempt_repo = revival_attempt_repo
        self._penance_repo = penance_repo
        self._feather_repo = feather_repo
        self._anubis = anubis
        self._eulogy_service = eulogy_service
        self._notification_service = notification_service

    # ═════════════════════════════════════════════════════════════════
    #  1. KILL — Record a character death
    # ═════════════════════════════════════════════════════════════════

    async def kill(
        self,
        character: Character,
        cause: DeathCause,
    ) -> DeathRecord:
        """
        Record a character's death. Creates a DeathRecord, generates
        a eulogy, and sends notifications.

        This does NOT mutate HP — Anubis already set HP to 0 before
        calling the Reaper. The Reaper's job is to formalize the death.
        """
        is_permanent = cause == DeathCause.GHOSTING_30_DAYS

        record = DeathRecord.create(
            character_id=character.id,
            user_id=character.user_id,
            cause=cause,
            hp_at_death=character.hp,
            total_hours_in_life=round(character.total_study_minutes / 60, 1),
            consecutive_ghost_days_at_death=character.ghosting_days,
            rituals_used_at_death=character.rituals_used,
            longest_streak_at_death=character.longest_streak,
            is_permanent=is_permanent,
        )

        await self._death_record_repo.save(record)

        # Generate eulogy
        eulogy = await self._eulogy_service.generate(
            character_id=character.id,
            user_id=character.user_id,
            death_record_id=record.id,
        )
        record.mark_eulogy_generated(eulogy.id)
        await self._death_record_repo.update(record)

        # Notification
        if is_permanent:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.PERMANENT_DEATH,
                title="Permanent Death",
                body="Your character has permanently fallen. The eulogy preserves their memory.",
                data={"character_id": str(character.id), "death_record_id": str(record.id)},
            )
        else:
            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.DEATH,
                title="Character Died",
                body="Your character has fallen. Revival paths are available.",
                data={"character_id": str(character.id), "death_record_id": str(record.id)},
            )

        return record

    # ═════════════════════════════════════════════════════════════════
    #  2. ELIGIBILITY CHECKS
    # ═════════════════════════════════════════════════════════════════

    # (check_ritual_eligibility removed — rituals no longer exist)

    async def check_penance_eligibility(self, character: Character) -> bool:
        """
        Can the character start a penance streak?
        Requirements: dead, not permanently dead, no active penance.
        """
        if not character.is_dead:
            return False
        if character.is_permanently_dead:
            return False
        active = await self._penance_repo.find_active_for_character(character.id)
        return active is None

    async def check_feather_eligibility(self, character: Character) -> bool:
        """
        Can the character be revived with a Phoenix Feather?
        Requirements: dead, not permanently dead, user has an available feather.
        """
        if not character.is_dead:
            return False
        if character.is_permanently_dead:
            return False
        count = await self._feather_repo.count_available_for_user(character.user_id)
        return count > 0

    # ═════════════════════════════════════════════════════════════════
    #  3. PHOENIX FEATHER REVIVAL
    # ═════════════════════════════════════════════════════════════════

    async def revive_with_feather(
        self, character: Character
    ) -> RevivalAttempt:
        """
        Instant revival using a Phoenix Feather (premium currency).
        Does NOT count against the ritual limit.
        """
        if not character.is_dead:
            raise CharacterNotDeadException()
        if character.is_permanently_dead:
            raise PermanentlyDeadException()

        feather = await self._feather_repo.find_available_for_user(character.user_id)
        if feather is None:
            raise NoAvailableFeatherException()

        death_record = await self._death_record_repo.find_latest_for_character(
            character.id
        )
        if death_record is None:
            raise DeathRecordNotFoundException()

        # Consume the feather
        feather.use(character.id)
        await self._feather_repo.update(feather)

        # Delegate HP restoration to Anubis
        await self._anubis.revive_with_phoenix_feather(character)

        # Record the attempt
        attempt = RevivalAttempt.create_success(
            character_id=character.id,
            death_record_id=death_record.id,
            method=RevivalMethod.PHOENIX_FEATHER,
            hp_restored_to=self.REVIVE_HP,
        )
        await self._revival_attempt_repo.save(attempt)

        await self._notification_service.send(
            user_id=character.user_id,
            notification_type=NotificationType.LIFE_SHIELD_USED,
            title="Phoenix Feather Used!",
            body=f"Your character has been revived at {self.REVIVE_HP} HP!",
            data={"character_id": str(character.id)},
        )

        return attempt

    # ═════════════════════════════════════════════════════════════════
    #  4. PENANCE STREAK
    # ═════════════════════════════════════════════════════════════════

    async def start_penance(
        self, character: Character
    ) -> PenanceStreak:
        """
        Begin a penance streak — user must hit 100% of their daily goal
        for 7 consecutive days while in ghost state to earn a free revival.
        """
        if not character.is_dead:
            raise CharacterNotDeadException()
        if character.is_permanently_dead:
            raise PermanentlyDeadException()

        existing = await self._penance_repo.find_active_for_character(character.id)
        if existing is not None:
            raise PenanceAlreadyActiveException()

        death_record = await self._death_record_repo.find_latest_for_character(
            character.id
        )
        if death_record is None:
            raise DeathRecordNotFoundException()

        attempt_count = await self._penance_repo.count_attempts_for_character(
            character.id
        )

        penance = PenanceStreak.start(
            character_id=character.id,
            death_record_id=death_record.id,
            attempt_number=attempt_count + 1,
        )
        await self._penance_repo.save(penance)

        await self._notification_service.send(
            user_id=character.user_id,
            notification_type=NotificationType.RITUAL_AVAILABLE,
            title="Penance Streak Started",
            body=f"Hit 100% of your daily goal for {self.PENANCE_REQUIRED_DAYS} consecutive days to revive.",
            data={"character_id": str(character.id), "penance_id": str(penance.id)},
        )

        return penance

    async def check_penance_progress(
        self,
        character: Character,
        goal_hit: bool,
    ) -> PenanceStreak:
        """
        Called daily by the cron to update penance progress.
        If goal_hit is False, the penance fails.
        If all required days are completed, the character is revived.
        """
        penance = await self._penance_repo.find_active_for_character(character.id)
        if penance is None:
            raise NoPenanceActiveException()

        if not goal_hit:
            character.clear_penance()
            penance.record_day_failure()
            await self._penance_repo.update(penance)

            # Record failed revival attempt
            attempt = RevivalAttempt.create_failure(
                character_id=character.id,
                death_record_id=penance.death_record_id,
                method=RevivalMethod.PENANCE_STREAK,
                reason=f"Missed goal on day {penance.days_completed + 1} of {penance.required_days}.",
            )
            await self._revival_attempt_repo.save(attempt)

            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.TREND_WARNING,
                title="Penance Failed",
                body="You missed your goal. The penance streak is broken.",
                data={"character_id": str(character.id)},
            )

            return penance

        # Goal hit — advance the streak
        completed = penance.record_day_success()
        await self._penance_repo.update(penance)

        if completed:
            character.clear_penance()
            # Revive the character via Anubis
            await self._anubis.revive_with_phoenix_feather(character)

            attempt = RevivalAttempt.create_success(
                character_id=character.id,
                death_record_id=penance.death_record_id,
                method=RevivalMethod.PENANCE_STREAK,
                hp_restored_to=self.REVIVE_HP,
            )
            await self._revival_attempt_repo.save(attempt)

            await self._notification_service.send(
                user_id=character.user_id,
                notification_type=NotificationType.STREAK_MILESTONE,
                title="Penance Complete!",
                body=f"7 days of discipline! Your character is revived at {self.REVIVE_HP} HP!",
                data={"character_id": str(character.id)},
            )

        return penance

    # (Re-engagement ritual methods removed — revival is now Phoenix Feather only)

    # ═════════════════════════════════════════════════════════════════
    #  6. UNFAIR DEATH RESTORATION
    # ═════════════════════════════════════════════════════════════════

    async def restore_unfair_death(
        self,
        character: Character,
        death_record: DeathRecord,
        compensation_hp: int = 100,
    ) -> RevivalAttempt:
        """
        Restore a character that died due to server error, crash, or
        verified unfair circumstances. Does NOT count against ritual limit.
        Restores full HP by default.
        """
        from character_domain.domain.value_objects.hp_change_result import HPChangeReason

        if character.is_permanently_dead:
            # Even permanent death can be reversed for unfair deaths
            character._is_permanently_dead = False

        # Reset ghost state and restore HP through Anubis
        character._ghosting_days = 0
        character._hp = 0
        character._touch()

        await self._anubis.change_hp(
            character,
            compensation_hp,
            HPChangeReason.REVIVAL,
            f"Unfair death restoration — compensated to {compensation_hp} HP.",
        )

        attempt = RevivalAttempt.create_success(
            character_id=character.id,
            death_record_id=death_record.id,
            method=RevivalMethod.UNFAIR_DEATH,
            hp_restored_to=compensation_hp,
        )
        await self._revival_attempt_repo.save(attempt)

        await self._notification_service.send(
            user_id=character.user_id,
            notification_type=NotificationType.LIFE_SHIELD_USED,
            title="Unfair Death Reversed",
            body=f"We detected an unfair death. Your character has been restored to {compensation_hp} HP.",
            data={"character_id": str(character.id)},
        )

        return attempt

    # ═════════════════════════════════════════════════════════════════
    #  7. QUERY METHODS
    # ═════════════════════════════════════════════════════════════════

    async def get_death_history(
        self, character_id: uuid.UUID
    ) -> list[DeathRecord]:
        """Get all death records for a character."""
        return await self._death_record_repo.find_all_for_character(character_id)

    async def get_revival_history(
        self, character_id: uuid.UUID
    ) -> list[RevivalAttempt]:
        """Get all revival attempts for a character."""
        return await self._revival_attempt_repo.find_all_for_character(character_id)

    async def get_active_penance(
        self, character_id: uuid.UUID
    ) -> Optional[PenanceStreak]:
        """Get the active penance streak (if any)."""
        return await self._penance_repo.find_active_for_character(character_id)

    async def get_revival_options(
        self, character: Character
    ) -> dict:
        """
        Returns all available revival options for a dead character.
        Revival paths: Phoenix Feather (instant) or Penance Streak (7-day grind).
        """
        if not character.is_dead:
            return {"available": False, "reason": "Character is not dead."}

        if character.is_permanently_dead:
            return {
                "available": False,
                "reason": "Character is permanently dead.",
                "can_restore_unfair": True,
            }

        penance_eligible = await self.check_penance_eligibility(character)
        feather_eligible = await self.check_feather_eligibility(character)
        feather_count = await self._feather_repo.count_available_for_user(
            character.user_id
        )

        active_penance = await self._penance_repo.find_active_for_character(
            character.id
        )

        return {
            "available": True,
            "penance_eligible": penance_eligible,
            "active_penance": (
                {
                    "id": str(active_penance.id),
                    "days_completed": active_penance.days_completed,
                    "days_remaining": active_penance.days_remaining,
                    "progress_pct": active_penance.progress_pct,
                }
                if active_penance
                else None
            ),
            "feather_eligible": feather_eligible,
            "feathers_available": feather_count,
        }
