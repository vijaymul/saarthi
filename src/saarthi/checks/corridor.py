"""
Check 4: Path Relevance & Walking Corridor Geometric Filter.
Filters out irrelevant peripheral objects and checks if hazard occupies the active walkable corridor.
"""

from ..sensors import CheckVote, SensingWindow

# Normalized camera frame corridor boundaries [xmin, xmax]
# Center 50% of the horizontal field of view corresponds to the ~1.0m walking corridor
CORRIDOR_XMIN: float = 0.25
CORRIDOR_XMAX: float = 0.75


def check_corridor(window: SensingWindow) -> CheckVote:
    """
    Determines whether detected objects overlap with the active walking corridor.
    """
    if not window.frames:
        return CheckVote(
            check_name="corridor",
            passed=True,
            confidence=0.5,
            reason="No frame data to evaluate walking corridor"
        )

    in_corridor_objects = []

    for frame in window.frames:
        for det in frame.detections:
            # Check bounding box overlap with corridor [0.25, 0.75]
            overlap_xmin = max(det.xmin, CORRIDOR_XMIN)
            overlap_xmax = min(det.xmax, CORRIDOR_XMAX)

            if overlap_xmax > overlap_xmin:
                # Object is inside walking corridor
                in_corridor_objects.append((det.class_name, det.depth_meters, det.center_x))

    if not in_corridor_objects:
        return CheckVote(
            check_name="corridor",
            passed=True,
            confidence=0.92,
            reason="Walking corridor is unobstructed; detections are purely peripheral"
        )

    obj_name, depth, cx = in_corridor_objects[0]
    return CheckVote(
        check_name="corridor",
        passed=False,
        confidence=0.88,
        reason=f"Object '{obj_name}' occupies walking corridor (center_x={cx:.2f}, depth={depth:.1f}m)",
        metadata={
            "in_corridor_objects": in_corridor_objects
        }
    )
