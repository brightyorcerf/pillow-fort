"""
Internal API routes — used by cron expressions and backend utilities.
These endpoints should be protected in production (VPC only, API key, etc.).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from character_domain.application.use_cases.run_daily_cron import RunDailyCronUseCase
from character_domain.presentation.dependencies.use_case_dependencies import (
    get_run_daily_cron_use_case,
)
from character_domain.domain.exceptions import CharacterDomainException

router = APIRouter(prefix="/internal", tags=["Internal"])


class CronTargetRequest(BaseModel):
    character_id: uuid.UUID


@router.post(
    "/cron/daily",
    summary="Daily cron — process evaluating and penance tracking",
    include_in_schema=False,
)
async def process_daily_cron(
    body: CronTargetRequest,
    use_case: RunDailyCronUseCase = Depends(get_run_daily_cron_use_case),
) -> dict[str, Any]:
    """
    Midnight cron job.
    Called externally by a job scheduler for each active character.
    """
    try:
        today = datetime.now(timezone.utc).date()
        result = await use_case.execute(body.character_id, today)
        return {"status": "ok", "processed": result}
    except CharacterDomainException as e:
        raise HTTPException(status_code=400, detail=e.detail)
