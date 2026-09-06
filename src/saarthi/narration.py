"""
On-Device LLM Narration & Conversational Guidance Layer.
Explains the deterministic hazard verdict in plain, natural spoken language.
"""

from typing import List, Optional
from .sensors import HazardState


class NarrationEngine:
    """Generates natural language audio guidance based on state machine output."""

    def generate_guidance(
        self,
        state: HazardState,
        primary_hazard: Optional[str],
        distance: float,
        failed_checks: List[str],
        clean_count: int = 0
    ) -> str:
        hazard_name = (primary_hazard or "obstacle").replace("_", " ")

        if state == HazardState.CLEAR:
            return "Path clear for four meters. Continue forward safely."

        elif state == HazardState.CAUTION:
            if "distance" in failed_checks or "corridor" in failed_checks:
                return f"Caution. {hazard_name.capitalize()} near path at {distance:.1f} meters. Slow your pace."
            return f"Caution. {hazard_name.capitalize()} detected nearby."

        elif state == HazardState.HAZARD:
            if "trajectory" in failed_checks:
                return f"Hazard! Approaching {hazard_name} closing in at {distance:.1f} meters. Step aside immediately."
            elif distance <= 1.0:
                return f"Stop! Imminent {hazard_name} directly in path at {distance:.1f} meters."
            else:
                return f"Hazard in path. {hazard_name.capitalize()} detected {distance:.1f} meters ahead. Adjust path left."

        elif state == HazardState.RECOVERING:
            return f"Path re-clearing. Confirming safe corridor (window {clean_count} of 5)."

        return "Guidance active."
