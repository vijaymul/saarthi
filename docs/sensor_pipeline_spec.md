# Saarthi Sensor Pipeline Specification

This document specifies the real-time sensor processing pipeline for **Saarthi on iQOO Devices**, detailing data flow, sampling rates, ring buffers, and Qualcomm Snapdragon NPU acceleration.

---

## 1. Hardware Sensor Suite

| Sensor Subsystem | Android API / Subsystem | Sampling Rate | Purpose |
| :--- | :--- | :--- | :--- |
| **Camera Feed** | Android `CameraX` (YUV_420_888) | 30–60 FPS | Real-time object detection & monocular depth |
| **IMU Linear Accel** | `Sensor.TYPE_LINEAR_ACCELERATION` | 50 Hz (20ms) | User velocity & motion trajectory vector |
| **IMU Gyroscope** | `Sensor.TYPE_GYROSCOPE` | 50 Hz (20ms) | Heading delta & phone tilt compensation |
| **Magnetometer** | `Sensor.TYPE_ROTATION_VECTOR` | 25 Hz (40ms) | Cardinal orientation & absolute heading |
| **Microphone** | `AudioRecord` (PCM 16-bit 16kHz) | Continuous (100ms buffer) | Ambient acoustic level & wake-word listening |

---

## 2. On-Device NPU Acceleration (Phase 2 Target Specification)

- **Target Device**: iQOO 12 (Qualcomm Snapdragon 8 Gen 3)
- **Model**: Quantized `YOLOv5n-INT8` (1.9M parameters, 4.2 MB size).
- **Inference Runtime**: TensorFlow Lite with `TFLite-Hexagon-Delegate` targeting the Snapdragon Hexagon NPU.
- **Target Inference Latency**: **~16.2 ms** (up to 60 FPS throughput).
- **Thermal Budget**: <+0.5°C over 30-minute run.
- **RAM Footprint**: ~138 MB peak resident memory.

---

## 3. The 6-Stage Real-Time Pipeline

```
[1. Capture (CameraX + IMU)]
            ↓
[2. Object Detection (YOLOv5n INT8 on Snapdragon NPU)]
            ↓
[3. Monocular Depth Estimation]
            ↓
[4. Walking Corridor Geometric Projection]
            ↓
[5. Alert Priority (Deterministic State Machine)]
            ↓
[6. Spoken Guidance (Local TTS) & Directional 4D Haptics]
```

---

## 4. Multi-Frame Ring Buffering

To defeat single-frame false positives, detections are stored in a rolling 10-frame ring buffer (330ms history at 30 FPS). A hazard alert only fires when the detection persists across $\ge 60\%$ of the buffered frames, ensuring transient reflections, motion blur, or camera glitches are suppressed.
