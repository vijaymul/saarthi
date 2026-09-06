"""
Deterministic Alert State Machine for Saarthi.
Controls safety transitions: CLEAR, CAUTION, HAZARD, RECOVERING.
Enforces the grumpy recovery rule (5 consecutive clean windows) and instant relapse.
"""

from typing import List, Optional
from .sensors import HazardState, HazardVerdict, CheckVote, SensingWindow
from .fusion import FusionEngine
from .narration import NarrationEngine


class HazardStateMachine:
    """
    Deterministic state machine for hazard awareness.
    The LLM never gets final authority; all transitions are controlled by deterministic threshold rules.
    """

    REQUIRED_CLEAN_WINDOWS_FOR_RECOVERY = 5

    def __init__(self):
        self.current_state: HazardState = HazardState.CLEAR
        self.clean_windows_count: int = 0
        self.fusion_engine = FusionEngine()
        self.narration_engine = NarrationEngine()

    def process_window(self, window: SensingWindow) -> HazardVerdict:
        """
        Processes a sensing window and transitions state deterministically.
        """
        all_votes, failed_checks, primary_hazard, closest_distance = self.fusion_engine.evaluate_window(window)
        num_failures = len(failed_checks)

        # High confidence check failure check
        has_critical_failure = any(
            v.confidence >= 0.85 for v in all_votes if not v.passed and v.check_name in ("distance", "trajectory", "taxonomy")
        )

        # Evaluate Next State
        if self.current_state == HazardState.CLEAR:
            if num_failures == 0:
                next_state = HazardState.CLEAR
                self.clean_windows_count = 0
            elif num_failures <= 2 and not has_critical_failure:
                next_state = HazardState.CAUTION
                self.clean_windows_count = 0
            else:
                next_state = HazardState.HAZARD
                self.clean_windows_count = 0

        elif self.current_state == HazardState.CAUTION:
            if num_failures == 0:
                next_state = HazardState.CLEAR
                self.clean_windows_count = 0
            elif num_failures >= 3 or has_critical_failure:
                next_state = HazardState.HAZARD
                self.clean_windows_count = 0
            else:
                next_state = HazardState.CAUTION
                self.clean_windows_count = 0

        elif self.current_state == HazardState.HAZARD:
            if num_failures == 0:
                # Begin recovery - never transition directly from HAZARD to CLEAR!
                self.clean_windows_count = 1
                next_state = HazardState.RECOVERING
            else:
                # Still in hazard
                self.clean_windows_count = 0
                next_state = HazardState.HAZARD

        elif self.current_state == HazardState.RECOVERING:
            if num_failures == 0:
                self.clean_windows_count += 1
                if self.clean_windows_count >= self.REQUIRED_CLEAN_WINDOWS_FOR_RECOVERY:
                    # Fully recovered!
                    next_state = HazardState.CLEAR
                    self.clean_windows_count = 0
                else:
                    # Keep recovering
                    next_state = HazardState.RECOVERING
            else:
                # Relapse during recovery! Drop straight back to HAZARD
                self.clean_windows_count = 0
                next_state = HazardState.HAZARD

        self.current_state = next_state

        # Generate on-device LLM natural voice guidance context
        guidance = self.narration_engine.generate_guidance(
            state=self.current_state,
            primary_hazard=primary_hazard,
            distance=closest_distance,
            failed_checks=failed_checks,
            clean_count=self.clean_windows_count
        )

        return HazardVerdict(
            state=self.current_state,
            primary_hazard=primary_hazard if num_failures > 0 else None,
            distance_meters=closest_distance if num_failures > 0 else 4.5,
            guidance_text=guidance,
            failed_checks=failed_checks,
            all_votes=all_votes,
            confidence=0.95
        )
