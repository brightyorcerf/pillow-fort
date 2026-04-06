from __future__ import annotations

import uuid

from character_domain.application.dtos import CharacterAnalyticsResponse
from character_domain.application.use_cases.get_pvr import GetPvrUseCase
from character_domain.application.use_cases.get_hp_timeline import GetHPTimelineUseCase
from character_domain.application.use_cases.get_hp_summary import GetHPSummaryUseCase
from character_domain.application.use_cases.get_weekly_consistency import GetWeeklyConsistencyUseCase


class GetAnalyticsUseCase:
    def __init__(
        self,
        get_pvr: GetPvrUseCase,
        get_hp_timeline: GetHPTimelineUseCase,
        get_hp_summary: GetHPSummaryUseCase,
        get_weekly_consistency: GetWeeklyConsistencyUseCase,
    ) -> None:
        self._get_pvr = get_pvr
        self._get_hp_timeline = get_hp_timeline
        self._get_hp_summary = get_hp_summary
        self._get_weekly_consistency = get_weekly_consistency

    async def execute(self, character_id: uuid.UUID) -> CharacterAnalyticsResponse:
        pvr = await self._get_pvr.execute(character_id)
        
        # Get last 50 HP timeline entries
        timeline = await self._get_hp_timeline.execute(str(character_id), limit=50, offset=0)
        
        # Get current day summary
        summary = await self._get_hp_summary.execute(character_id)
        
        # Get weekly consistency
        consistency = await self._get_weekly_consistency.execute(character_id)

        return CharacterAnalyticsResponse(
            pvr=pvr,
            timeline=timeline.entries,       # Unpack list directly from HPTimelineResponse
            consistency=consistency,
            hp_summary=summary,
        )
