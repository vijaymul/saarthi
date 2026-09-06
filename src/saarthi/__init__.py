"""
Saarthi: Real-time Hazard Detection & Multi-Sensor Fusion Engine for iQOO Devices.
100% On-Device AI with Deterministic Safety Authority.
"""

from .sensors import (
    BoundingBox,
    CameraFrame,
    ImuSample,
    AudioContextSample,
    SensingWindow,
    HazardVerdict,
    HazardState
)
from .fusion import FusionEngine
from .state_machine import HazardStateMachine
from .narration import NarrationEngine

__version__ = "0.1.0"
__all__ = [
    "BoundingBox",
    "CameraFrame",
    "ImuSample",
    "AudioContextSample",
    "SensingWindow",
    "HazardVerdict",
    "HazardState",
    "FusionEngine",
    "HazardStateMachine",
    "NarrationEngine",
]
