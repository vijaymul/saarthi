# Saarthi: Real-Time On-Device Hazard Detection for the Visually Impaired

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo%20Video-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/MLpM2aX246M?si=EFiSEgVJ4zKq2G_P)
[![Live Mobile Prototype](https://img.shields.io/badge/Live%20Prototype-Vercel%20App-00F0FF?style=for-the-badge)](https://saarthi-swart.vercel.app)
[![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passing-2DD4BF?style=for-the-badge)](https://github.com/vijaymul/saarthi)
[![Target Platform](https://img.shields.io/badge/Target-iQOO%2012%20%7C%20Snapdragon%20NPU-FF6600?style=for-the-badge)](https://github.com/vijaymul/saarthi)

> **Working Proof of Concept (PoC) demonstrating the core multi-sensor hazard detection and deterministic alert pipeline.**

---

## ⚡ At a Glance

| Question | Answer |
| :--- | :--- |
| **What?** | **Saarthi** detects physical hazards (vehicles, pedestrians, curb drops, poles) in the walking path of visually impaired users. |
| **Why?** | Cloud solutions (*Be My Eyes, Seeing AI*) fail without internet and have high latency. Expensive wearables (*OrCam*) cost $4,000+. Saarthi runs **100% on-device** on accessible smartphones. |
| **How?** | Computer vision + motion vectors + **6 deterministic consistency checks** + 4-state aviation safety machine. |
| **Does it work?** | **Yes.** Working Python PoC with **14/14 passing automated tests** (0.012s), synthetic trace simulator, and mobile interactive prototype. |
| **Can I run it?** | `python examples/run_demo.py` & `python -m unittest discover tests -v` |

---

## 📋 PoC Evidence Summary

- ✅ **14/14 automated unit & integration tests passing** (Python `unittest`, 0.012s execution)
- ✅ **Deterministic 4-State Alert Engine** with **5-window recovery hysteresis**
- ✅ **6 Independent Sensing-Consistency Checks** (Taxonomy, Distance, Trajectory, Corridor, Persistence, Ambient)
- ✅ **Multi-Frame Persistence Filter** eliminating single-frame detector false alarms
- ✅ **Offline-First Architecture** with zero cloud round-trips
- ✅ **Live Mobile Prototype & 2:30 Product Walkthrough** available

📺 **[Watch the Product Video Demo on YouTube](https://youtu.be/MLpM2aX246M?si=EFiSEgVJ4zKq2G_P)**  
📱 **[Launch the Live Mobile Web Prototype](https://saarthi-swart.vercel.app)**

---

## 🔍 Proof of Concept (PoC) Architecture

Saarthi separates **physical safety decisions** from **conversational voice guidance**:

```
Camera / Sensor Input
        ↓
Object Detection & Depth Heuristic
        ↓
Motion & Trajectory Vector Analysis
        ↓
Walking Corridor Spatial Filter (3D Path)
        ↓
Temporal Multi-Frame Persistence Filter
        ↓
Deterministic Safety State Machine (100% Alert Authority)
        ↓
Spoken Guidance (Context Only) & Earcon Tone
```

### State Machine Lifecycle
The safety engine enforces a strict **recovery hysteresis** to prevent rapid `HAZARD ↔ CLEAR` oscillation:

$$\text{CLEAR} \longrightarrow \text{CAUTION} \longrightarrow \text{HAZARD} \overset{\text{Clean Frame}}{\longrightarrow} \text{RECOVERING (5 Windows)} \longrightarrow \text{CLEAR}$$

- **No Instant Clears**: Once a `HAZARD` is triggered, the system requires **5 consecutive clean sensing windows (hysteresis)** to return to `CLEAR`.
- **Instant Relapse**: Any new obstacle during `RECOVERING` immediately drops back to `HAZARD` and resets the recovery window counter to 0.

---

## 🧠 Critical Architecture: Safety Layer vs. LLM

> 🛡️ **"Saarthi does not ask an LLM whether an obstacle is dangerous. The deterministic safety layer makes that decision; the language model only converts the resulting state into contextual guidance."**

```
┌────────────────────────────────────────────────────────┐
│             DETERMINISTIC SAFETY LAYER                 │
│  - 6 Mathematical Consistency Checks                   │
│  - 4-State Transition Logic with Hysteresis            │
│  - 100% ALERT & SAFETY AUTHORITY                       │
└──────────────────────────┬─────────────────────────────┘
                           │ (Emits Verified Verdict)
                           ▼
┌────────────────────────────────────────────────────────┐
│              LLM / SPOKEN GUIDANCE LAYER               │
│  - Generates conversational spatial description        │
│  - Contextual explanation ONLY                         │
│  - Zero ability to override or suppress alerts         │
└────────────────────────────────────────────────────────┘
```

This aviation-safety architecture ensures hallucinations or LLM latency **never** compromise user physical safety.

---

## 📊 Technical Status: Measured vs. Implemented vs. Target

| Feature / Metric | Status | Technical Details |
| :--- | :---: | :--- |
| **Multi-Sensor Fusion (6 Checks)** | **Implemented** | Taxonomy, Safe-Stop Distance, Trajectory, Walking Corridor, Temporal Persistence, Ambient Context. |
| **Deterministic State Machine** | **Implemented** | 4 states (`CLEAR`, `CAUTION`, `HAZARD`, `RECOVERING`) with 5-window recovery hysteresis. |
| **False-Positive Suppression** | **Measured** | Single-frame detector flickers suppressed (1/10 frames < 60% threshold = rejected). |
| **Test Suite Execution** | **Measured** | **14 / 14 unit & integration tests passed** in **0.012s** (Python standard library `unittest`). |
| **Interactive Mobile Prototype** | **Implemented** | Mobile-first HUD, 4 interactive scenarios, Web Audio frequency earcons, speech synthesis. |
| **NPU Inference Latency** | **Target (Phase 2)** | Target **~16.2 ms** INT8 quantized YOLO model on Qualcomm Snapdragon Hexagon NPU. |
| **Real-time CameraX Stream** | **Target (Phase 2)** | Target **60 FPS** camera analysis on native Android iQOO 12 deployment. |
| **Directional 4D Haptics** | **Target (Phase 2)** | Dual-motor localized pulse patterns via Android VibrationEffect API. |

---

## 🧪 Automated Test Verification

All 14 tests execute deterministically with zero third-party dependencies:

```bash
python -m unittest discover tests -v
```

### Verified Test Matrix

| Test Suite | Test Case | Scenario Description | Result |
| :--- | :--- | :--- | :---: |
| `test_checks.py` | `test_taxonomy_check_clean` | Clean frame without hazard classes passes | **PASS** |
| `test_checks.py` | `test_taxonomy_check_hazard_detected` | Auto-rickshaw triggers taxonomy violation | **PASS** |
| `test_checks.py` | `test_distance_check_safe_vs_critical` | 4.0m passes; 1.2m flags CRITICAL | **PASS** |
| `test_checks.py` | `test_trajectory_check_approaching` | Closing velocity vector (>0.3 m/s) flags | **PASS** |
| `test_checks.py` | `test_corridor_check_in_path_vs_peripheral` | Center corridor flags; peripheral passes | **PASS** |
| `test_checks.py` | `test_persistence_check_suppresses_flicker` | Single-frame flicker suppressed; multi-frame flags | **PASS** |
| `test_checks.py` | `test_ambient_check_lighting_and_audio` | Gain calibrations for low light & street noise | **PASS** |
| `test_state_machine.py` | `test_clean_stay_clear` | Clean trace stays in CLEAR continuously | **PASS** |
| `test_state_machine.py` | `test_hazard_trigger_and_no_direct_clear` | HAZARD must enter RECOVERING first | **PASS** |
| `test_state_machine.py` | `test_recovery_hysteresis_requires_five_clean_windows` | HAZARD requires 5 consecutive clean windows | **PASS** |
| `test_state_machine.py` | `test_relapse_during_recovery` | Relapse resets recovery count and drops to HAZARD | **PASS** |
| `test_integration.py` | `test_clean_trace_end_to_end` | Honest walking trace produces clean states | **PASS** |
| `test_integration.py` | `test_hazard_scenario_full_lifecycle` | End-to-end multi-hazard lifecycle verification | **PASS** |
| `test_integration.py` | `test_anti_flicker_suppression` | Full trace false-positive rejection test | **PASS** |

---

## 🚀 Running the PoC Locally

### 1. Run the Python PoC Demo:
```bash
python examples/run_demo.py
```

### 2. Run the Test Suite:
```bash
python -m unittest discover tests -v
```

### 3. Run the Mobile Web Prototype:
```bash
python -m http.server 8080
# Open http://localhost:8080/index.html on desktop or mobile
```

---

## ⚠️ Current Limitations & Safety Disclaimer

1. **PoC Evaluation Scope**: The current validation is executed over deterministic synthetic and recorded street traces modeling Indian urban navigation scenarios.
2. **Phase 2 Native Hardware Integration**: The native Android application (CameraX + Qualcomm Snapdragon Hexagon NPU pipeline) is scheduled for the next deployment milestone.
3. **Distance Heuristics**: The PoC uses camera perspective and bounding box scaling for distance estimation; full native production will utilize hardware-accelerated depth estimation.
4. **Safety Disclaimer**: Saarthi is an assistive AI prototype designed for obstacle awareness and is **NOT** a replacement for a white cane, guide dog, or trained human assistance.

---

## 👨‍💻 Builder & Team Identity

- **Project**: Saarthi
- **Team**: **Team Straw Head**
- **Solo Builder**: **Abhijeet Dubey**
- **GitHub Handle**: [@vijaymul](https://github.com/vijaymul)
- **Repository**: [https://github.com/vijaymul/saarthi](https://github.com/vijaymul/saarthi)
- **Contact**: [dubeyvijay8983@gmail.com](mailto:dubeyvijay8983@gmail.com)

> 💡 **Note for Hackathon Judges**: The official project and submission team is **Abhijeet Dubey (Solo Builder / Team Straw Head)**. The codebase is hosted under the personal GitHub profile **[@vijaymul](https://github.com/vijaymul)**.
