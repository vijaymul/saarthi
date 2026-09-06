"""
Deterministic synthetic sensor trace generator for validation and testing.
"""

from typing import List
from .sensors import (
    BoundingBox,
    CameraFrame,
    ImuSample,
    AudioContextSample,
    SensingWindow,
)


def create_window(
    start_time: float,
    end_time: float,
    fps: int = 10,
    detections_per_frame: List[List[BoundingBox]] = None,
    heading_deg: float = 90.0,
    walking_speed: float = 1.2,
    db_level: float = 55.0,
    luminance: float = 0.8
) -> SensingWindow:
    """Creates a synthetic sensing window with synchronized frames and IMU samples."""
    num_frames = max(1, int((end_time - start_time) * fps))
    frames: List[CameraFrame] = []
    imu_samples: List[ImuSample] = []
    audio_samples: List[AudioContextSample] = []

    dt = (end_time - start_time) / num_frames

    for i in range(num_frames):
        t = start_time + (i * dt)
        dets = []
        if detections_per_frame and i < len(detections_per_frame):
            dets = detections_per_frame[i]
        elif detections_per_frame and len(detections_per_frame) == 1:
            dets = detections_per_frame[0]

        frames.append(CameraFrame(timestamp=t, frame_id=i + 1, detections=dets, luminance=luminance))
        imu_samples.append(ImuSample(timestamp=t, accel_x=0.01, accel_y=0.05, accel_z=9.81, heading_deg=heading_deg, walking_speed_mps=walking_speed))
        audio_samples.append(AudioContextSample(timestamp=t, db_level=db_level, is_high_noise=(db_level > 70)))

    return SensingWindow(start_time=start_time, end_time=end_time, frames=frames, imu_samples=imu_samples, audio_samples=audio_samples)


def generate_clean_trace(num_windows: int = 10, window_len_sec: float = 2.0) -> List[SensingWindow]:
    """Generates an honest walking trace where path is clear throughout."""
    windows = []
    for w in range(num_windows):
        t0 = w * window_len_sec
        t1 = t0 + window_len_sec
        windows.append(create_window(t0, t1))
    return windows


def generate_hazard_scenario_trace() -> List[SensingWindow]:
    """
    Generates a realistic sequence:
    Windows 0-2: Clear walking
    Windows 3-4: Approaching Auto-Rickshaw hazard injected (2.1m -> 1.2m closing in corridor)
    Windows 5-9: Clear path (Triggering the 5-window recovery sequence)
    Window 10: Relapse! Low curb step-down obstacle injected
    Windows 11-15: Final clean recovery sequence
    """
    windows = []
    # Windows 0-2: Clean
    for w in range(3):
        t0 = w * 2.0
        windows.append(create_window(t0, t0 + 2.0))

    # Window 3: Approaching auto-rickshaw (d=2.1m)
    t0 = 6.0
    dets_w3 = [
        BoundingBox("auto_rickshaw", 0.98, ymin=0.3, xmin=0.35, ymax=0.8, xmax=0.65, depth_meters=2.1)
    ]
    windows.append(create_window(t0, t0 + 2.0, detections_per_frame=[dets_w3]))

    # Window 4: Approaching closer (d=1.2m, closing vector)
    t0 = 8.0
    dets_w4 = [
        BoundingBox("auto_rickshaw", 0.99, ymin=0.2, xmin=0.3, ymax=0.9, xmax=0.7, depth_meters=1.2)
    ]
    windows.append(create_window(t0, t0 + 2.0, detections_per_frame=[dets_w4]))

    # Windows 5-9: Path cleared (5 recovery windows)
    for i, w in enumerate(range(5, 10)):
        t0 = w * 2.0
        windows.append(create_window(t0, t0 + 2.0))

    # Window 10: Relapse! Curb step down (d=0.8m)
    t0 = 20.0
    dets_w10 = [
        BoundingBox("step_down", 0.95, ymin=0.7, xmin=0.3, ymax=0.95, xmax=0.7, depth_meters=0.8)
    ]
    windows.append(create_window(t0, t0 + 2.0, detections_per_frame=[dets_w10]))

    # Windows 11-15: Final recovery
    for w in range(11, 16):
        t0 = w * 2.0
        windows.append(create_window(t0, t0 + 2.0))

    return windows


def generate_single_frame_flicker_trace() -> List[SensingWindow]:
    """Generates a window with a single-frame glitch/flicker that should be suppressed by Check 5."""
    t0 = 0.0
    t1 = 2.0
    # 10 frames total: only frame 2 has a spurious glitch detection, rest 9 frames are clean
    dets_per_frame = [[] for _ in range(10)]
    dets_per_frame[2] = [
        BoundingBox("vehicle", 0.85, ymin=0.2, xmin=0.4, ymax=0.8, xmax=0.6, depth_meters=1.5)
    ]
    return [create_window(t0, t1, fps=5, detections_per_frame=dets_per_frame)]
