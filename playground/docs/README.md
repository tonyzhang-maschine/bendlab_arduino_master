# JQ Glove Visualization - Documentation

**Last Updated:** October 25, 2025 (Post User Testing)  
**Version:** MVP v1.2

---

## 📖 **Documentation Navigation**

### 🚀 **Start Here**
1. **[../README.md](../README.md)** - Main project README (in playground root)
2. **[QUICK_START.md](QUICK_START.md)** - How to run the application
3. **[STATUS.md](STATUS.md)** - ⭐ Current status and resolved issues
4. **[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)** - ⭐ **Performance limitations (MUST READ!)**

---

## 📊 **Current Status Documents**

### Essential Reading:
- **[STATUS.md](STATUS.md)** - Overall system status, resolved issues
- **[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)** - ⚠️ **Performance limitations from user testing**
  - ~3 second visualization lag
  - ~5 Hz actual display FPS
  - Window resize flickering
  - Root cause analysis
  - Optimization roadmap

### Quick Reference:
- **[QUICK_START.md](QUICK_START.md)** - Usage instructions
- **[START_HERE.md](START_HERE.md)** - Quick orientation for new developers

---

## 🔧 **Technical Documentation**

### Architecture & Design:
- **[realtime_vis_plan.md](realtime_vis_plan.md)** - Original architecture design
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level project overview

### Issue Resolution Details:
- **[ISSUE_1_FIX_SUMMARY.md](ISSUE_1_FIX_SUMMARY.md)** - Visualization color fix (dynamic range)
- **[ISSUE_3_FIX_SUMMARY.md](ISSUE_3_FIX_SUMMARY.md)** - GUI freezing fix (sequential processing)

### Release Notes:
- **[WHATS_NEW_v1.1.md](WHATS_NEW_v1.1.md)** - Changes in v1.1 (Issue #1 fix)

---

## 📁 **Documentation Organization**

```
playground/
├── README.md                       ← Main entry point
├── realtime_glove_viz.py          ← Main application
├── (other code files...)
│
├── docs/                           ← All current documentation
│   ├── README.md                   ← This file
│   ├── STATUS.md                   ← Current status
│   ├── KNOWN_LIMITATIONS.md        ← Performance limitations ⭐
│   ├── QUICK_START.md              ← Usage guide
│   ├── START_HERE.md               ← Quick orientation
│   ├── DOCUMENTATION_INDEX.md      ← Detailed index
│   ├── PROJECT_SUMMARY.md          ← Project overview
│   ├── realtime_vis_plan.md        ← Architecture
│   ├── ISSUE_1_FIX_SUMMARY.md      ← Fix details
│   ├── ISSUE_3_FIX_SUMMARY.md      ← Fix details
│   └── WHATS_NEW_v1.1.md           ← Release notes
│
└── archive/
    ├── (legacy code files...)
    └── deprecated_docs/            ← Older documentation
        ├── README_REALTIME.md
        └── COMPATIBILITY_UPDATE.md
```

---

## 🎯 **Documentation by Purpose**

### For First-Time Users:
1. [../README.md](../README.md) - Project overview
2. [QUICK_START.md](QUICK_START.md) - How to run
3. [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) - What to expect

### For Developers:
1. [STATUS.md](STATUS.md) - Current state
2. [realtime_vis_plan.md](realtime_vis_plan.md) - Architecture
3. [ISSUE_1_FIX_SUMMARY.md](ISSUE_1_FIX_SUMMARY.md) - Fix details
4. [ISSUE_3_FIX_SUMMARY.md](ISSUE_3_FIX_SUMMARY.md) - Fix details

### For Troubleshooting:
1. [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) - Known issues
2. [STATUS.md](STATUS.md) - System status
3. [QUICK_START.md](QUICK_START.md) - Troubleshooting section

### For Understanding Performance:
1. [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) - ⭐ **Must read!**
2. [ISSUE_3_FIX_SUMMARY.md](ISSUE_3_FIX_SUMMARY.md) - Sequential processing
3. [realtime_vis_plan.md](realtime_vis_plan.md) - Original design

---

## ⚠️ **Important Notes**

### Known Limitations (From User Testing):
The system has **documented performance limitations**:
- **~3 second visualization lag**
- **~5 Hz actual display FPS** (not 10 Hz)
- **Window resize flickering**

**These are NOT bugs**, but performance constraints of the current implementation.

**See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) for:**
- Detailed root cause analysis
- Why this happens
- Optimization roadmap
- Quick fixes to try
- Suitable vs unsuitable use cases

### System is Suitable For:
- ✅ Data logging and recording
- ✅ Offline analysis
- ✅ Sensor validation
- ✅ Development/testing

### NOT Suitable For (without optimization):
- ❌ Real-time control systems
- ❌ Time-critical applications
- ❌ Gesture recognition
- ❌ Interactive real-time feedback

---

## 📚 **Complete Documentation Index**

For a detailed breakdown of all documentation files, see:
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)**

---

## 🔗 **External References**

### Hardware Documentation:
- Device Specification: `../【矩侨精密】织物电子皮肤产品规格书250630-V1.1.pdf`
- Sensor Data Table: `../Copy of 【矩侨精密】160-1024全床传感器ADC压强数据表 241113.xlsx`

### Code Reference:
- `../sensor_mapping.py` - Complete sensor-to-index mapping
- `../realtime_glove_viz.py` - Main application
- `../hand_visualizer.py` - Visualization widget
- `../serial_reader.py` - Serial communication
- `../glove_parser.py` - Data parsing

---

## 📞 **Getting Help**

### If you have issues:
1. Check [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) - Is this a known limitation?
2. Check [STATUS.md](STATUS.md) - Is this a resolved issue?
3. Check [QUICK_START.md](QUICK_START.md) - Troubleshooting section
4. Run test scripts in playground root

### Performance Issues:
See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) for:
- Detailed analysis of performance bottlenecks
- Optimization suggestions
- Quick fixes to try
- Expected vs actual performance

---

**Version:** MVP v1.2  
**Status:** Production Ready (with documented limitations)  
**Last Updated:** October 25, 2025

