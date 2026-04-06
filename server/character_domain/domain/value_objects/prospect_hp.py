"""
Unified HP Equation — PRD §3.1.5 Prospect Theory-Based HP System.

Implements the core HP calculation grounded in Prospect Theory
(loss aversion) and Goal-Setting Theory (ambition rewards).

The equation has a +5 HP y-axis shift so that perfectly meeting
your goal earns +5 HP (not zero).

Key variables:
  A (Actual Time): Total active study time today.
  G (Goal Time): Target goal committed for today.
  V (PVR Baseline): Rolling 14-day average study time.
  λ (Loss Aversion): 2.25 — losses feel 2.25× worse than gains.

Final daily HP change:
  ΔHP = max(-33, min(25, (HP_raw + 5) × M))

Where:
  If A ≥ G:  HP_raw = 25 × (A/G - 1)^0.88
  If A < G:  HP_raw = -25 × λ × (1 - A/G)^0.88

  M (Goal Difficulty Multiplier):
    G > V:  M = 1 + 0.5 × (G/V - 1)     (stretch — rewards ambition)
    G = V:  M = 1.0                       (baseline)
    G < V:  M = 1 - 0.3 × (1 - G/V)      (sandbagging — suppresses gain)
"""

from __future__ import annotations

from dataclasses import dataclass

# ── Constants ──────────────────────────────────────────────────────────

LOSS_AVERSION_LAMBDA = 2.25
EXPONENT = 0.88
MAX_HP_GAIN = 25
MAX_HP_LOSS = -33
BASE_SUCCESS_OFFSET = 5  # +5 HP y-axis shift
ONBOARDING_BASELINE_MINUTES = 30  # Fallback V for Day-1 users


# ── Result ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProspectHPResult:
    """Immutable result of the Prospect Theory HP calculation."""

    hp_raw: float
    """Raw HP before multiplier and clamping (includes +5 offset)."""

    multiplier_m: float
    """Goal difficulty multiplier (anti-sandbagging)."""

    unclamped: float
    """hp_raw × multiplier_m, before final clamping."""

    final_delta: int
    """Final HP change after clamping to [-33, +25]."""

    goal_met: bool
    """Whether the user met or exceeded their goal."""

    description: str
    """Human-readable explanation of the HP change."""


# ── Core Equation ──────────────────────────────────────────────────────

def compute_prospect_hp(
    actual_minutes: int,
    goal_minutes: int,
    pvr_baseline_minutes: float,
    loss_aversion: float = LOSS_AVERSION_LAMBDA,
    onboarding_baseline: int = ONBOARDING_BASELINE_MINUTES,
) -> ProspectHPResult:
    """
    Compute the daily HP change using the Prospect Theory equation.

    Args:
        actual_minutes: A — total active time studied today.
        goal_minutes: G — the committed goal for today (must be > 0).
        pvr_baseline_minutes: V — rolling 14-day average study time.
        loss_aversion: λ — hardcoded to 2.25.
        onboarding_baseline: Fallback V on Day 1 (no history).

    Returns:
        ProspectHPResult with the final clamped HP delta.

    Raises:
        ValueError: If goal_minutes <= 0 (must be blocked by UI).
    """
    if goal_minutes <= 0:
        raise ValueError(
            "Goal must be > 0 minutes. The UI must enforce "
            "the minimum goal floor."
        )

    # Zero-Division Guard: Day-1 user with no 14-day history
    v = pvr_baseline_minutes if pvr_baseline_minutes > 0 else onboarding_baseline

    g = float(goal_minutes)
    a = float(max(0, actual_minutes))

    # ── Component 1: Base Performance (Prospect Theory Curves) ──
    goal_met = a >= g

    if goal_met:
        # User hit or exceeded goal
        ratio = (a / g) - 1.0  # 0 when A == G
        hp_base = MAX_HP_GAIN * (ratio ** EXPONENT) if ratio > 0 else 0.0
    else:
        # User missed goal — loss aversion amplifies
        shortfall = 1.0 - (a / g)
        hp_base = -MAX_HP_GAIN * loss_aversion * (shortfall ** EXPONENT)

    # Apply +5 HP y-axis shift
    hp_raw = hp_base + BASE_SUCCESS_OFFSET

    # ── Component 2: Goal Difficulty Multiplier (Anti-Sandbagging) ──
    if g > v:
        # Stretch goal — rewards ambition
        m = 1.0 + 0.5 * ((g / v) - 1.0)
    elif g < v:
        # Sandbagging — suppresses HP gain
        m = 1.0 - 0.3 * (1.0 - (g / v))
    else:
        # Baseline goal
        m = 1.0

    # ── Final Clamping ──
    unclamped = hp_raw * m
    final_delta = int(max(MAX_HP_LOSS, min(MAX_HP_GAIN, unclamped)))

    # ── Description ──
    if goal_met:
        if a == g:
            desc = (
                f"Hit goal exactly ({int(a)}/{int(g)} min) — "
                f"+{final_delta} HP."
            )
        else:
            pct_over = int(((a / g) - 1) * 100)
            desc = (
                f"Exceeded goal by {pct_over}% ({int(a)}/{int(g)} min) — "
                f"+{final_delta} HP."
            )
    else:
        pct_done = int((a / g) * 100)
        desc = (
            f"Studied {int(a)}/{int(g)} min ({pct_done}%) — "
            f"{final_delta} HP."
        )

    return ProspectHPResult(
        hp_raw=round(hp_raw, 2),
        multiplier_m=round(m, 3),
        unclamped=round(unclamped, 2),
        final_delta=final_delta,
        goal_met=goal_met,
        description=desc,
    )
