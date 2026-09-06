"""
Data structures representing raw sensor signals, detections, and fused windows.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class HazardState(str, Enum):
    CLEAR = "CLEAR"
    CAUTION = "CAUTION"
    HAZARD = "HAZARD"
    RECOVERING = "RECOVERING"


@dataclass(frozen=True)
class BoundingBox:
    """Detected object bounding box with confidence and monocular depth."""
    class_name: str
    confidence: float
    ymin: float
    xmin: float
    ymax: float
    xmax: float
    depth_meters: float

    @property
    def center_x(self) -> float:
        return (self.xmin + self.xmax) / 2.0

    @property
    def center_y(self) -> float:
        return (self.ymin + self.ymax) / 2.0

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin


@dataclass(frozen=True)
class CameraFrame:
    """A single frame from CameraX processed by on-device YOLOv5n."""
    timestamp: float
    frame_id: int
    detections: List[BoundingBox] = field(default_factory=list)
    luminance: float = 0.8  # 0.0 (pitch black) to 1.0 (bright daylight)


@dataclass(frozen=True)
class ImuSample:
    """IMU motion sample from Android SensorManager."""
    timestamp: float
    accel_x: float  # lateral acceleration (m/s^2)
    accel_y: float  # forward acceleration (m/s^2)
    accel_z: float  # vertical acceleration (m/s^2)
    heading_deg: float  # Compass heading (0-360)
    walking_speed_mps: float = 1.2  # Estimated pedestrian walking speed (m/s)


@dataclass(frozen=True)
class AudioContextSample:
    """Ambient acoustic sample from local audio cue listener."""
    timestamp: float
    db_level: float = 55.0  # Decibels
    is_high_noise: bool = False


@dataclass
class CheckVote:
    """Result of an individual sensing consistency check."""
    check_name: str
    passed: bool
    confidence: float  # 0.0 to 1.0
    reason: str
    metadata: dict = field(default_factory=dict)


@dataclass
class SensingWindow:
    """Synchronized window of multi-modal sensor frames over a duration."""
    start_time: float
    end_time: float
    frames: List[CameraFrame] = field(default_factory=list)
    imu_samples: List[ImuSample] = field(default_factory=list)
    audio_samples: List[AudioContextSample] = field(default_factory=list)


@dataclass
class HazardVerdict:
    """Final output emitted by the Saarthi state machine."""
    state: HazardState
    primary_hazard: Optional[str]
    distance_meters: float
    guidance_text: str
    failed_checks: List[str] = field(default_factory=list)
    all_votes: List[CheckVote] = field(default_factory=list)
    confidence: float = 0.95
