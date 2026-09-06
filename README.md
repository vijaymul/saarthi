# Saarthi: Real-time Hazard Detection for the Visually Impaired on iQOO Devices

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo%20Video-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/MLpM2aX246M?si=EFiSEgVJ4zKq2G_P)
[![iQOO Device AI](https://img.shields.io/badge/Device-iQOO_12-FF6600?style=for-the-badge&logo=android)](https://github.com/vijaymul/saarthi)
[![Snapdragon NPU](https://img.shields.io/badge/NPU-Snapdragon_8_Gen_3-0070BA?style=for-the-badge&logo=qualcomm)](https://github.com/vijaymul/saarthi)
[![100% On-Device](https://img.shields.io/badge/Privacy-100%25_On--Device-2DD4BF?style=for-the-badge)](https://github.com/vijaymul/saarthi)

> **"Awareness before contact. Your Eyes. Your Voice. Your Guide."**

📺 **[Watch the Full Product Demo on YouTube](https://youtu.be/MLpM2aX246M?si=EFiSEgVJ4zKq2G_P)**

Saarthi is an on-device accessibility system built during a 30-hour hackathon sprint that detects physical hazards by fusing real-time computer vision and motion sensing on iQOO devices. Designed specifically for the **70+ million visually impaired people in India**, Saarthi provides instant spatial awareness without requiring internet connectivity or cloud processing.

---

## 🌟 Key Capabilities

1. **Deterministic Multi-Sensor Fusion**:
   - CameraX real-time capture (60 FPS)
   - Quantized YOLOv5n hazard detector running on the **Qualcomm Snapdragon Hexagon NPU** via TensorFlow Lite (16.2ms inference latency)
   - IMU velocity vectors and monocular depth estimation

2. **6 Independent Sensing Consistency Checks**:
   - **Object Taxonomy**: Identifies vehicles, pedestrians, low curbs, poles, and overhead hazards
   - **Distance vs Safe-Stop Threshold**: Monocular depth calculation for walking speeds
   - **Motion Trajectory**: Heading and closing velocity vector analysis
   - **Path Relevance**: Spatial filtering restricted to the user's active walking corridor
   - **Temporal Persistence**: Corroborates hazards across N consecutive frames to eliminate single-frame false positives
   - **Ambient Context**: Auto-calibrates audio gain and camera exposure for dusk and ambient street noise

3. **4 Real-Time Verdict States**:
   - `CLEAR`: Unobstructed path for >4.5m (Confidence >0.94)
   - `CAUTION`: Object closing near path edge
   - `HAZARD`: Direct collision path within alert radius (Quarantine route)
   - `RECOVERING`: Path re-clearing and revalidating

4. **Aviation-Safety Architecture**:
   - **Deterministic Layer (100% Alert Authority)**: Controls all hazard alarms and physical safety decisions
   - **On-Device LLM Layer (Context Only)**: Generates natural conversational spoken guidance; never overrides deterministic safety checks

5. **100% Offline & Private**:
   - Zero cloud round-trips
   - Zero internet permissions required (`Airplane Mode: Verified`)
   - 100% free and on-device (no recurring subscriptions or specialized $4,000+ wearables)

---

## 🏗️ 6-Stage Real-Time Pipeline

```
[1. Capture (CameraX)] 
       ↓
[2. Object Detection (YOLOv5n on Snapdragon NPU)] 
       ↓
[3. Distance Estimation (Monocular Depth)] 
       ↓
[4. Path Relevance (Corridor Filtering)] 
       ↓
[5. Alert Priority (Deterministic State Machine)] 
       ↓
[6. Spoken Guidance & Directional 4D Haptics]
```

---

## 🚀 Running the Proof-of-Concept (PoC)

### 1. Run the Python PoC Demo:
```bash
# Run the end-to-end multi-sensor fusion demo
python examples/run_demo.py
```

### 2. Run the Test Suite (14 Tests, 100% Standard Library):
```bash
# Execute unit tests & synthetic trace validations
python -m unittest discover tests -v
```

---

## 📱 Running the Live Mobile Web Prototype Locally:

```bash
# Start local HTTP server
python -m http.server 8080

# Open in your browser (or mobile device)
http://localhost:8080/index.html
```

---

## 📊 Competitive Analysis

| Solution | Offline Ready | Motion + Depth Fusion | <200ms Latency | 100% On-Device | Free / No Subscription |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Be My Eyes** | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Seeing AI** | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Aira** | ✗ | ✗ | ✗ | ✗ | ✗ |
| **OrCam MyEye** | ✓ | ✗ | ✗ | ✓ | ✗ ($4,000+) |
| **SAARTHI (iQOO)** | **✓ (100% Offline)** | **✓ (6 Checks)** | **✓ (16.2ms)** | **✓ (Snapdragon NPU)** | **✓ (Free)** |

---

## 👨‍💻 Builder & Credits

- **Project**: Saarthi (Team Impact)
- **Solo Builder**: **Abhijeet Dubey**
- **Email**: [dubeyvijay8983@gmail.com](mailto:dubeyvijay8983@gmail.com)
- **Repository**: [https://github.com/vijaymul/saarthi](https://github.com/vijaymul/saarthi)
