"""
Check 1: Object Taxonomy & Hazard Classification.
Evaluates detected object classes against the physical mobility hazard taxonomy.
"""

from typing import Set
from ..sensors import CheckVote, SensingWindow

# Ground-truth hazard classes relevant for visually impaired street navigation
HAZARD_CLASSES: Set[str] = {
    "vehicle", "car", "auto_rickshaw", "rickshaw", "bus", "truck", "motorcycle", "scooter", "bicycle",
    "pedestrian", "person",
    "pole", "pillar", "lamp_post", "tree_trunk", "low_branch",
    "stairs_down", "stairs_up", "curb", "step_down", "pothole", "trench", "construction_barrier"
}

# High severity classes requiring immediate quarantine
HIGH_SEVERITY_CLASSES: Set[str] = {
    "vehicle", "car", "auto_rickshaw", "rickshaw", "bus", "truck", "motorcycle", "scooter",
    "stairs_down", "pothole", "trench"
}


def check_taxonomy(window: SensingWindow) -> CheckVote:
    """
    Evaluates whether any detected object matches a known hazard class in the taxonomy.
    """
    if not window.frames:
        return CheckVote(
            check_name="taxonomy",
            passed=True,
            confidence=0.5,
            reason="No camera frames in window (insufficient data)"
        )

    detected_hazards = []
    max_confidence = 0.0
    highest_severity = False

    for frame in window.frames:
        for det in frame.detections:
            cls_lower = det.class_name.lower()
            if cls_lower in HAZARD_CLASSES:
                detected_hazards.append(cls_lower)
                if det.confidence > max_confidence:
                    max_confidence = det.confidence
                if cls_lower in HIGH_SEVERITY_CLASSES:
                    highest_severity = True

    if not detected_hazards:
        return CheckVote(
            check_name="taxonomy",
            passed=True,
            confidence=0.95,
            reason="No known hazardous object taxonomy classes detected"
        )

    # Found hazard classes
    primary = detected_hazards[0]
    return CheckVote(
        check_name="taxonomy",
        passed=False,
        confidence=max_confidence,
        reason=f"Hazard class '{primary}' detected in taxonomy (high_severity={highest_severity})",
        metadata={
            "detected_classes": list(set(detected_hazards)),
            "high_severity": highest_severity
        }
    )
