"""
Check 2: Distance Estimation & Safe-Stop Reaction Threshold.
Compares monocular depth estimate against walking reaction thresholds.
"""

from ..sensors import CheckVote, SensingWindow

# Reaction thresholds based on normal pedestrian walking speed (1.2 m/s)
# Safe reaction distance: d = v_walk * t_reaction + d_safety = 1.2 * 1.5 + 0.7 = 2.5 meters
CAUTION_DISTANCE_METERS: float = 3.0
CRITICAL_DISTANCE_METERS: float = 1.8
IMMINENT_COLLISION_METERS: float = 0.9


def check_distance(window: SensingWindow) -> CheckVote:
    """
    Evaluates whether any detected object violates the safe-stop walking distance threshold.
    """
    if not window.frames:
        return CheckVote(
            check_name="distance",
            passed=True,
            confidence=0.5,
            reason="No detections to estimate distance"
        )

    min_distance = float('inf')
    closest_object = None

    for frame in window.frames:
        for det in frame.detections:
            if det.depth_meters < min_distance:
                min_distance = det.depth_meters
                closest_object = det.class_name

    if min_distance == float('inf') or min_distance > CAUTION_DISTANCE_METERS:
        return CheckVote(
            check_name="distance",
            passed=True,
            confidence=0.92,
            reason=f"All objects beyond safe distance threshold ({min_distance:.1f}m > {CAUTION_DISTANCE_METERS:.1f}m)"
        )

    # Object within alert radius
    if min_distance <= IMMINENT_COLLISION_METERS:
        confidence = 0.99
        severity = "IMMINENT"
    elif min_distance <= CRITICAL_DISTANCE_METERS:
        confidence = 0.92
        severity = "CRITICAL"
    else:
        confidence = 0.80
        severity = "CAUTION"

    return CheckVote(
        check_name="distance",
        passed=False,
        confidence=confidence,
        reason=f"Object '{closest_object}' at {min_distance:.1f}m violates {severity} safe-stop threshold ({CRITICAL_DISTANCE_METERS:.1f}m)",
        metadata={
            "min_distance_meters": min_distance,
            "severity": severity
        }
    )
