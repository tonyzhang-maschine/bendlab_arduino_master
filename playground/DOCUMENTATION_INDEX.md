# JQ Glove Playground - Documentation Index

**Quick Navigation:** Documentation organized by purpose and priority.

---

## 🚀 **Start Here**

### For First-Time Users
1. **[README.md](README.md)** - Project overview, hardware specs, protocol details
2. **[QUICK_START.md](QUICK_START.md)** - How to run the application
3. **[STATUS.md](STATUS.md)** - **⭐ Current status, known issues, and progress**

### For Developers
1. **[realtime_vis_plan.md](realtime_vis_plan.md)** - Architecture and design decisions
2. **[COMPATIBILITY_UPDATE.md](COMPATIBILITY_UPDATE.md)** - Recent sensor mapping updates
3. **[sensor_mapping.py](sensor_mapping.py)** - Complete sensor index reference

---

## 📊 **Current Status Documents**

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| **[STATUS.md](STATUS.md)** | Current progress, known issues, next steps | Oct 24, 2025 |
| **[QUICK_START.md](QUICK_START.md)** | Quick reference for running the app | Oct 24, 2025 |

**Status Summary:**
- ✅ Serial communication working
- ✅ Statistics display working  
- 🔴 Visualization colors not updating (Issue #1)
- 🟡 Minor sensor mapping cross-talk (Issue #2)
- 🟡 Intermittent GUI freezing (Issue #3)

---

## 📚 **Technical Documentation**

### Core Documentation
- **[README.md](README.md)** - Main project documentation
  - Device specifications (JQ20-XL-11, 136 sensors)
  - Protocol details (delimiter, packet structure)
  - Sensor mapping overview
  - File descriptions

- **[realtime_vis_plan.md](realtime_vis_plan.md)** - Real-time visualization design
  - System architecture diagram
  - Library selection (PyQtGraph)
  - Threading model
  - Data flow
  - MVP implementation checklist

### Implementation Details
- **[COMPATIBILITY_UPDATE.md](COMPATIBILITY_UPDATE.md)** - Migration guide
  - Sensor mapping changes (162→136 sensors)
  - Code updates for documented indices
  - Breaking changes
  - Test results

- **[README_REALTIME.md](README_REALTIME.md)** - Original MVP guide
  - Installation instructions
  - Usage guide
  - Troubleshooting
  - Phase 2/3 roadmap

---

## 💻 **Code Reference**

### Main Application Files

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| **realtime_glove_viz.py** | Main GUI application | ~330 | ✅ Working |
| **hand_visualizer.py** | PyQtGraph visualization widget | ~280 | 🔴 Colors not updating |
| **serial_reader.py** | Serial reading thread | ~110 | ✅ Working |
| **glove_parser.py** | Packet parsing & frame assembly | ~160 | ✅ Working |
| **sensor_mapping.py** | Sensor-to-index mapping | ~190 | 🟡 Needs verification |

### Utility Scripts

| File | Purpose | Usage |
|------|---------|-------|
| **test_compatibility.py** | Comprehensive system test | `python test_compatibility.py` |
| **test_app_minimal.py** | Minimal GUI test | `python test_app_minimal.py` |

### Legacy/Analysis Scripts (Reference Only)

| File | Purpose | Note |
|------|---------|------|
| **jq_glove_capture.py** | Original capture script | ⚠️ Superseded by realtime_glove_viz.py |
| **analyze_glove_data.py** | Static data analysis | ⚠️ For offline .bin files |
| **visualize_raw_data.py** | Raw data heatmap | ⚠️ For debugging only |
| **quick_data_check.py** | Packet inspection | ⚠️ For debugging only |

---

## 🔧 **Testing & Debugging**

### Test Scripts
1. **test_compatibility.py** - Full system compatibility test
   ```bash
   python test_compatibility.py
   ```
   Tests: imports, parsing, sensor mapping, statistics

2. **test_app_minimal.py** - Minimal GUI test
   ```bash
   python test_app_minimal.py
   ```
   Tests: HandVisualizer, update_sensors, no IndexError

### Running the Application
```bash
# From playground directory
../.venv/bin/python realtime_glove_viz.py

# Expected output:
# - GUI window opens
# - Click "Start" to connect
# - Statistics update in real-time
```

### Debugging Known Issues
See **[STATUS.md](STATUS.md)** → "Debugging Guide" section for:
- Issue #1: Black dots (visualization not updating)
- Issue #2: Sensor cross-talk
- Issue #3: GUI freezing

---

## 📖 **Protocol & Hardware Reference**

### Packet Structure
```
[Delimiter: AA 55 03 99] [Packet Index] [Sensor Type] [Payload]
```

**Frame Composition:**
- Packet 0x01: 6 header + 128 payload = 134 bytes
- Packet 0x02: 6 header + 144 payload = 150 bytes
- **Total frame:** 272 bytes (128 + 144 payload)

### Sensor Mapping
See **[sensor_mapping.py](sensor_mapping.py)** for complete mapping:
- 136 unique sensors (12 per finger, 5 backs, 72 palm)
- Documented byte indices (not sequential!)
- Example: Thumb uses indices [19, 18, 17, 3, 2, 1, 243, ...]

### Data Regions
```
Indices 1-255:   Pressure sensor data (136 sensors)
Indices 256-271: IMU data (accelerometer/gyroscope)
```

---

## 🗂️ **File Organization**

```
playground/
├── 📱 Main Application
│   ├── realtime_glove_viz.py      # Main GUI app
│   ├── hand_visualizer.py         # Visualization widget
│   ├── serial_reader.py           # Serial thread
│   ├── glove_parser.py            # Packet parser
│   └── sensor_mapping.py          # Sensor indices
│
├── 📚 Documentation
│   ├── STATUS.md                  # ⭐ Current status
│   ├── DOCUMENTATION_INDEX.md     # This file
│   ├── README.md                  # Project overview
│   ├── QUICK_START.md             # Quick reference
│   ├── realtime_vis_plan.md       # Architecture
│   ├── COMPATIBILITY_UPDATE.md    # Migration guide
│   └── README_REALTIME.md         # Original MVP docs
│
├── 🧪 Testing
│   ├── test_compatibility.py      # System tests
│   └── test_app_minimal.py        # Minimal tests
│
└── 🔧 Legacy/Utilities (Reference)
    ├── jq_glove_capture.py        # Original capture
    ├── analyze_glove_data.py      # Offline analysis
    ├── visualize_raw_data.py      # Raw heatmaps
    └── quick_data_check.py        # Packet inspection
```

---

## 🎯 **Quick Links by Task**

### I want to...
- **Run the app** → [QUICK_START.md](QUICK_START.md)
- **Understand current issues** → [STATUS.md](STATUS.md)
- **Learn the architecture** → [realtime_vis_plan.md](realtime_vis_plan.md)
- **Fix visualization colors** → [STATUS.md#issue-1](STATUS.md)
- **Verify sensor mapping** → [sensor_mapping.py](sensor_mapping.py)
- **Debug packet parsing** → [glove_parser.py](glove_parser.py)
- **Test the system** → [test_compatibility.py](test_compatibility.py)

### I need...
- **Hardware specs** → [README.md](README.md) → "Hardware Connection"
- **Protocol details** → [README.md](README.md) → "Protocol & Data Format"
- **Sensor indices** → [sensor_mapping.py](sensor_mapping.py)
- **Performance metrics** → [STATUS.md](STATUS.md) → "Performance Metrics"
- **Known issues** → [STATUS.md](STATUS.md) → "Known Issues"

---

## 📋 **Documentation Maintenance**

### Update Frequency
- **STATUS.md** - Update after each major test or bug fix
- **QUICK_START.md** - Update when commands/setup changes
- **COMPATIBILITY_UPDATE.md** - Update when API changes
- **README.md** - Update when specs or features change

### Contribution Guidelines
When making changes, update:
1. Relevant code file
2. STATUS.md (if it affects known issues)
3. This index (if adding new files)
4. Version/date stamps

---

## 📞 **Support & Resources**

### Hardware Documentation
- **PDF:** `【矩侨精密】织物电子皮肤产品规格书250630-V1.1.pdf`
- **Product:** JQ20-XL-11 (Left Hand, 136 sensing points)
- **Manufacturer:** Weihai JQ Industries Technology Co., Ltd

### Dependencies
```bash
# Core dependencies
pip install pyserial numpy PyQt5 pyqtgraph

# Full requirements
pip install -r requirements.txt
```

### Getting Help
1. Check [STATUS.md](STATUS.md) for known issues
2. Review [QUICK_START.md](QUICK_START.md) troubleshooting
3. Run [test_compatibility.py](test_compatibility.py)
4. Check logs in GUI log panel

---

**Last Updated:** October 24, 2025  
**Current Version:** MVP v1.0  
**Status:** 🟡 Functional with known issues

