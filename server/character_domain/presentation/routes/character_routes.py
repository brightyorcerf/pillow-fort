"""
Character API routes — thin controllers delegating to use cases.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from character_domain.application.dtos import (
    CharacterStatusResponse,
    CompleteSessionRequest,
    CovenantResponse,
    CreateCharacterRequest,
    GoalValidationResponse,
    SessionCheckInRequest,
    SessionResponse,
    SetCovenantRequest,
    StartSessionRequest,
    ValidateGoalRequest,
    CharacterAnalyticsResponse,
    RevivalStatusResponse,
    RevivalRequest,
)
from character_domain.application.use_cases import (
    CompleteSessionUseCase,
    CreateCharacterUseCase,
    GetCharacterStatusUseCase,
    SessionCheckInUseCase,
    SetCovenantUseCase,
    StartSessionUseCase,
    ValidateGoalUseCase,
    GetAnalyticsUseCase,
    GetRevivalStatusUseCase,
    HandleRevivalUseCase,
)
from character_domain.domain.exceptions import (
    CharacterAlreadyDeadException,
    CharacterAlreadyExistsException,
    CharacterDomainException,
    CharacterNotFoundException,
    CharacterNotDeadException,
    CovenantAlreadyExistsException,
    CovenantNotSignedException,
    GoalAboveCeilingException,
    GoalBelowMinimumException,
    MaxRitualsExhaustedException,
    NoActiveRitualException,
    RitualRequiredException,
    SessionAlreadyActiveException,
    SessionNotFoundException,
)
from character_domain.presentation.dependencies.character_dependencies import (
    get_current_character_id,
    get_current_user_id,
)
from character_domain.presentation.dependencies.use_case_dependencies import (
    get_complete_session_use_case,
    get_create_character_use_case,
    get_character_status_use_case,
    get_session_check_in_use_case,
    get_set_covenant_use_case,
    get_start_session_use_case,
    get_validate_goal_use_case,
    get_analytics_use_case,
    get_revival_status_use_case,
    get_handle_revival_use_case,
)

router = APIRouter(prefix="/characters", tags=["Character"])


# ── Exception → HTTP status mapping ──────────────────────────────────

_EXCEPTION_STATUS_MAP: dict[type, int] = {
    CharacterNotFoundException: status.HTTP_404_NOT_FOUND,
    CharacterAlreadyExistsException: status.HTTP_409_CONFLICT,
    CharacterAlreadyDeadException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    CharacterNotDeadException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    MaxRitualsExhaustedException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    RitualRequiredException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    CovenantAlreadyExistsException: status.HTTP_409_CONFLICT,
    CovenantNotSignedException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    GoalBelowMinimumException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    GoalAboveCeilingException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    SessionAlreadyActiveException: status.HTTP_409_CONFLICT,
    SessionNotFoundException: status.HTTP_404_NOT_FOUND,
    NoActiveRitualException: status.HTTP_404_NOT_FOUND,
}


def _handle(exc: CharacterDomainException) -> HTTPException:
    code = _EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return HTTPException(status_code=code, detail=exc.detail)


# ═════════════════════════════════════════════════════════════════════
#  CHARACTER LIFECYCLE
# ═════════════════════════════════════════════════════════════════════


@router.post(
    "",
    response_model=CharacterStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new character (onboarding)",
)
async def create_character(
    body: CreateCharacterRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    use_case: CreateCharacterUseCase = Depends(get_create_character_use_case),
):
    try:
        return await use_case.execute(user_id, body)
    except CharacterDomainException as e:
        raise _handle(e)


@router.get(
    "/me",
    response_model=CharacterStatusResponse,
    summary="Get current character status",
)
async def get_character_status(
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: GetCharacterStatusUseCase = Depends(get_character_status_use_case),
):
    try:
        return await use_case.execute(character_id)
    except CharacterDomainException as e:
        raise _handle(e)


# ═════════════════════════════════════════════════════════════════════
#  COVENANT (DAILY COMMITMENT)
# ═════════════════════════════════════════════════════════════════════


@router.post(
    "/me/covenant",
    response_model=CovenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set today's covenant",
)
async def set_covenant(
    body: SetCovenantRequest,
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: SetCovenantUseCase = Depends(get_set_covenant_use_case),
):
    try:
        return await use_case.execute(character_id, body)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/me/covenant/validate",
    response_model=GoalValidationResponse,
    summary="Validate a goal before committing",
)
async def validate_goal(
    body: ValidateGoalRequest,
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: ValidateGoalUseCase = Depends(get_validate_goal_use_case),
):
    try:
        return await use_case.execute(character_id, body)
    except CharacterDomainException as e:
        raise _handle(e)


# ═════════════════════════════════════════════════════════════════════
#  STUDY SESSIONS
# ═════════════════════════════════════════════════════════════════════


@router.post(
    "/me/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a study session",
)
async def start_session(
    body: StartSessionRequest,
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: StartSessionUseCase = Depends(get_start_session_use_case),
):
    try:
        return await use_case.execute(character_id, body)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/me/sessions/complete",
    response_model=SessionResponse,
    summary="Complete an active study session",
)
async def complete_session(
    body: CompleteSessionRequest,
    use_case: CompleteSessionUseCase = Depends(get_complete_session_use_case),
):
    try:
        return await use_case.execute(body)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/me/sessions/check-in",
    summary="Random check-in verification",
)
async def session_check_in(
    body: SessionCheckInRequest,
    use_case: SessionCheckInUseCase = Depends(get_session_check_in_use_case),
):
    try:
        return await use_case.execute(body)
    except CharacterDomainException as e:
        raise _handle(e)


# ═════════════════════════════════════════════════════════════════════
#  COMPOSITE ANALYTICS
# ═════════════════════════════════════════════════════════════════════


@router.get(
    "/me/analytics",
    response_model=CharacterAnalyticsResponse,
    summary="Get comprehensive character analytics",
)
async def get_analytics(
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: GetAnalyticsUseCase = Depends(get_analytics_use_case),
):
    """
    Returns PVR, 50-entry HP timeline, weekly consistency stats, and daily summary.
    """
    try:
        return await use_case.execute(character_id)
    except CharacterDomainException as e:
        raise _handle(e)


# ═════════════════════════════════════════════════════════════════════
#  COMPOSITE REVIVAL
# ═════════════════════════════════════════════════════════════════════


@router.get(
    "/me/revival/status",
    response_model=RevivalStatusResponse,
    summary="Get full revival status and history",
)
async def get_revival_status(
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: GetRevivalStatusUseCase = Depends(get_revival_status_use_case),
):
    """
    Returns available revival options, active penance streaks, death history,
    revival history, and eulogies in one payload.
    """
    try:
        return await use_case.execute(character_id)
    except CharacterDomainException as e:
        raise _handle(e)


@router.post(
    "/me/revival",
    summary="Unified revival dispatcher",
)
async def handle_revival(
    body: RevivalRequest,
    character_id: uuid.UUID = Depends(get_current_character_id),
    use_case: HandleRevivalUseCase = Depends(get_handle_revival_use_case),
) -> dict[str, Any]:
    """
    Handles all interactions with revival mechanics (start/advance/complete ritual, feather).
    """
    try:
        return await use_case.execute(character_id, body)
    except CharacterDomainException as e:
        raise _handle(e)
