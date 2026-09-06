"""
Check 6: Ambient Context & Dynamic Environmental Calibration.
Evaluates ambient lighting and acoustic noise to adaptively adjust alert sensitivity and gain.
"""

from ..sensors import CheckVote, SensingWindow

LOW_LIGHT_THRESHOLD: float = 0.25
HIGH_NOISE_DB_THRESHOLD: float = 75.0  # Busy Indian street / traffic


def check_ambient(window: SensingWindow) -> CheckVote:
    """
    Evaluates ambient lighting and acoustic context.
    Always passes, but provides adaptive context flags and sensitivity calibrations.
    """
    avg_luminance = 0.8
    if window.frames:
        avg_luminance = sum(f.luminance for f in window.frames) / len(window.frames)

    avg_db = 55.0
    if window.audio_samples:
        avg_db = sum(a.db_level for a in window.audio_samples) / len(window.audio_samples)

    is_low_light = avg_luminance < LOW_LIGHT_THRESHOLD
    is_high_noise = avg_db >= HIGH_NOISE_DB_THRESHOLD

    reasons = []
    if is_low_light:
        reasons.append(f"Low light ({avg_luminance:.2f}) -> Enhanced edge contrast mode")
    if is_high_noise:
        reasons.append(f"High street noise ({avg_db:.1f} dB) -> Boost TTS speech volume & 4D haptic intensity")

    if not reasons:
        reasons.append(f"Optimal conditions (Lum: {avg_luminance:.2f}, Audio: {avg_db:.1f} dB)")

    return CheckVote(
        check_name="ambient",
        passed=True,
        confidence=0.95,
        reason="; ".join(reasons),
        metadata={
            "avg_luminance": avg_luminance,
            "avg_db": avg_db,
            "is_low_light": is_low_light,
            "is_high_noise": is_high_noise,
            "boost_audio": is_high_noise
        }
    )
