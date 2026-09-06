# Android Integration Plan (30-Hour Hackathon Roadmap)

This document details the hour-by-hour deployment strategy for porting the Python Proof-of-Concept to a native Android application on iQOO devices.

---

## 30-Hour Build Milestones

### Phase 1: Foundation (Hours 0–6)
- Setup Android Studio project with `CameraX` Preview & ImageAnalysis use cases.
- Implement `SensorManager` listeners for Linear Acceleration and Rotation Vector.
- Establish `Vivo Office Kit` phone-laptop bridge for real-time live screen mirroring and ADB telemetry.
- **Deliverable**: Live camera + IMU data feed running synchronously on iQOO handset.

### Phase 2: Core Detection Engine (Hours 6–12)
- Quantize `YOLOv5n` to INT8 using TFLite Model Maker.
- Wire `Hexagon NPU Delegate` for Snapdragon hardware acceleration.
- Implement the 6 sensing consistency checks in Kotlin.
- **Deliverable**: 16ms on-device object detection with hazard taxonomy matching.

### Phase 3: Sensor Fusion & State Machine (Hours 12–18)
- Port the deterministic 4-state alert machine (`CLEAR`, `CAUTION`, `HAZARD`, `RECOVERING`).
- Implement the 5-window grumpy recovery rule and instant relapse logic.
- Integrate on-device LLM narration layer for conversational speech output.
- **Deliverable**: End-to-end hazard verdict state machine running locally on device.

### Phase 4: Audio, Haptics & UI Polish (Hours 18–24)
- Integrate Android `TextToSpeech` engine (Offline English/Hindi voice models).
- Add directional spatial earcons and iQOO 4D game vibration haptic feedback.
- Build high-contrast accessible UI with large touch targets and talkback semantics.
- **Deliverable**: Complete audio/haptic feedback loop with zero cloud roundtrips.

### Phase 5: Verification & Demo Polish (Hours 24–30)
- Benchmark real-world battery drain, thermal throttling, and inference latency.
- Validate against 40 recorded hazard clips (auto-rickshaws, potholes, crowded markets).
- Finalize demo video and documentation.
- **Deliverable**: Native APK deployed on iQOO 12 device ready for judging.
