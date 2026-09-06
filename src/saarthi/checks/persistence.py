"""
Check 5: Temporal Persistence & Multi-Frame Consistency.
Requires hazard detection to persist across N consecutive frames, defeating single-frame false-positive flickers.
"""

from collections import Counter
from ..sensors import CheckVote, SensingWindow

MIN_PERSISTENCE_RATIO: float = 0.6  # Hazard must appear in at least 60% of window frames


def check_persistence(window: SensingWindow) -> CheckVote:
    """
    Evaluates whether hazard detections are corroborated across time rather than a single-frame glitch.
    """
    total_frames = len(window.frames)
    if total_frames < 2:
        return CheckVote(
            check_name="persistence",
            passed=True,
            confidence=0.5,
            reason="Single frame window - cannot evaluate temporal persistence"
        )

    # Count appearances of each object class across frames
    class_frame_counts = Counter()
    for frame in window.frames:
        unique_classes_in_frame = {det.class_name.lower() for det in frame.detections}
        for cls_name in unique_classes_in_frame:
            class_frame_counts[cls_name] += 1

    if not class_frame_counts:
        return CheckVote(
            check_name="persistence",
            passed=True,
            confidence=0.95,
            reason="Clean window with no transient flickers"
        )

    # Check most persistent class
    most_common_class, count = class_frame_counts.most_common(1)[0]
    persistence_ratio = count / total_frames

    if persistence_ratio >= MIN_PERSISTENCE_RATIO:
        # Confirmed persistent hazard
        return CheckVote(
            check_name="persistence",
            passed=False,
            confidence=min(0.99, 0.70 + persistence_ratio * 0.3),
            reason=f"Hazard '{most_common_class}' persisted across {count}/{total_frames} frames ({persistence_ratio*100:.0f}%)",
            metadata={
                "persisted_class": most_common_class,
                "frame_count": count,
                "total_frames": total_frames
            }
        )
    else:
        # Transient flicker / glitch detected and suppressed!
        return CheckVote(
            check_name="persistence",
            passed=True,
            confidence=0.88,
            reason=f"Suppressed transient single-frame flicker '{most_common_class}' ({count}/{total_frames} frames < {MIN_PERSISTENCE_RATIO*100:.0f}%)",
            metadata={
                "flicker_suppressed": most_common_class,
                "frame_count": count,
                "total_frames": total_frames
            }
        )
