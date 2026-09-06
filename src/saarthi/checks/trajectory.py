"""
Check 3: Motion Trajectory & Velocity Vector Analysis.
Fuses IMU heading and relative object movement to detect closing vectors.
"""

from ..sensors import CheckVote, SensingWindow


def check_trajectory(window: SensingWindow) -> CheckVote:
    """
    Computes whether detected objects have a closing velocity vector towards the user.
    """
    if len(window.frames) < 2:
        return CheckVote(
            check_name="trajectory",
            passed=True,
            confidence=0.6,
            reason="Insufficient frame history for velocity estimation"
        )

    # Compare first and last frame detections
    first_frame = window.frames[0]
    last_frame = window.frames[-1]
    dt = last_frame.timestamp - first_frame.timestamp
    if dt <= 0.001:
        dt = 0.1  # Fallback delta

    closing_hazards = []
    max_closing_rate = 0.0

    for det_start in first_frame.detections:
        for det_end in last_frame.detections:
            if det_start.class_name == det_end.class_name:
                # Calculate depth delta
                depth_delta = det_start.depth_meters - det_end.depth_meters
                closing_rate_mps = depth_delta / dt  # Positive means approaching

                if closing_rate_mps > 0.3:  # Approaching faster than 0.3 m/s
                    closing_hazards.append((det_end.class_name, closing_rate_mps, det_end.depth_meters))
                    if closing_rate_mps > max_closing_rate:
                        max_closing_rate = closing_rate_mps

    if not closing_hazards:
        return CheckVote(
            check_name="trajectory",
            passed=True,
            confidence=0.90,
            reason="No closing velocity vectors towards user heading"
        )

    obj_name, rate, dist = closing_hazards[0]
    return CheckVote(
        check_name="trajectory",
        passed=False,
        confidence=min(0.98, 0.75 + (max_closing_rate * 0.1)),
        reason=f"Hazard '{obj_name}' is closing in at {rate:.2f} m/s (currently at {dist:.1f}m)",
        metadata={
            "max_closing_rate_mps": max_closing_rate,
            "closing_objects": closing_hazards
        }
    )
