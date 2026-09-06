"""
Multi-sensor fusion layer running all six checks over a synchronized window.
"""

from typing import List, Tuple, Optional
from .sensors import CheckVote, SensingWindow
from .checks import (
    check_taxonomy,
    check_distance,
    check_trajectory,
    check_corridor,
    check_persistence,
    check_ambient,
)


class FusionEngine:
    """Executes the 6 sensing checks in fixed deterministic order and produces votes."""

    CHECKS = [
        ("taxonomy", check_taxonomy),
        ("distance", check_distance),
        ("trajectory", check_trajectory),
        ("corridor", check_corridor),
        ("persistence", check_persistence),
        ("ambient", check_ambient),
    ]

    def evaluate_window(self, window: SensingWindow) -> Tuple[List[CheckVote], List[str], Optional[str], float]:
        """
        Runs all six checks against the window.
        Returns:
            all_votes: List of all 6 CheckVote objects.
            failed_check_names: List of names of checks that flagged a hazard.
            primary_hazard: The dominant hazard object name (if any).
            closest_distance: The closest distance observed in meters.
        """
        all_votes: List[CheckVote] = []
        failed_checks: List[str] = []
        primary_hazard: Optional[str] = None
        closest_distance: float = 99.0

        for name, check_fn in self.CHECKS:
            vote = check_fn(window)
            all_votes.append(vote)
            if not vote.passed:
                failed_checks.append(name)

        # Extract primary hazard and distance from window frames
        if window.frames:
            for frame in window.frames:
                for det in frame.detections:
                    if det.depth_meters < closest_distance:
                        closest_distance = det.depth_meters
                        primary_hazard = det.class_name

        return all_votes, failed_checks, primary_hazard, closest_distance
