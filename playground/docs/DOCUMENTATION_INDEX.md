# Documentation Index

Complete guide to JQ Glove Real-time Visualization System documentation.

**Last Updated:** October 25, 2025  
**Version:** MVP v1.3 + Sensor Mapping Tools

---

## 🚀 **Quick Start**

**New to the project? Start here:**

1. **[START_HERE.md](START_HERE.md)** - Quick orientation guide
2. **[QUICK_START.md](QUICK_START.md)** - How to run the application
3. **[STATUS.md](STATUS.md)** - Current status and what's working

---

## 📚 **Core Documentation**

### Project Overview
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level project overview
- **[STATUS.md](STATUS.md)** - ⭐ Current status, resolved issues, and progress
- **[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)** - Performance notes and considerations

### Usage Guides
- **[QUICK_START.md](QUICK_START.md)** - Quick reference for running the app
- **[README.md](README.md)** - Main documentation (in docs/)

### Architecture & Design
- **[realtime_vis_plan.md](realtime_vis_plan.md)** - Architecture and design decisions
- **[PERFORMANCE_OPTIMIZATION_v1.3.md](PERFORMANCE_OPTIMIZATION_v1.3.md)** - Performance improvements

### Release Notes
- **[WHATS_NEW_v1.3.md](WHATS_NEW_v1.3.md)** - Latest release notes (v1.3)
- **[CHANGELOG.md](CHANGELOG.md)** - Complete change history

---

## 🏷️ **Sensor Mapping Documentation** (`annotation/`)

Complete sensor mapping and data frame index assignment workflow:

### Annotation Workflow
- **[ANNOTATION_QUICKSTART.md](annotation/ANNOTATION_QUICKSTART.md)** - 5-minute quick start guide
- **[ANNOTATION_GUIDE.md](annotation/ANNOTATION_GUIDE.md)** - Detailed annotation workflow
- **[ANNOTATION_TOOL_SUMMARY.md](annotation/ANNOTATION_TOOL_SUMMARY.md)** - Technical overview

### Data Frame Index Assignment
- **[DATAFRAME_INDEX_ASSIGNMENT.md](annotation/DATAFRAME_INDEX_ASSIGNMENT.md)** - Complete mapping guide
  - Maps sensor_id → data_frame_index (byte positions)
  - Explains finger tips, bodies, and palm mapping strategy
  - Usage examples and integration guide

### Files Generated
- `glove_sensor_map_refined.csv` - Sensor coordinates (165 sensors)
- `glove_sensor_map_annotated.csv` - Sensors with regions (11 regions)
- `glove_sensor_map_with_indices.csv` - Complete mapping (162/165 sensors)

---

## 📦 **Archive** (`../archive/`)

### Legacy Scripts
- **[README_ARCHIVE.md](../archive/README_ARCHIVE.md)** - Overview of archived scripts
- `analyze_glove_data.py` - Offline data analysis
- `jq_glove_capture.py` - Simple capture script
- `visualize_raw_data.py` - Raw data visualization

### Deprecated Documentation (`deprecated_docs/`)
- **ISSUE_1_FIX_SUMMARY.md** - Visualization color fix (resolved)
- **ISSUE_3_FIX_SUMMARY.md** - Sequential processing fix (resolved)
- **WHATS_NEW_v1.1.md** - Old release notes (v1.1)
- **PERFORMANCE_IMPROVEMENTS_SUMMARY.md** - Superseded by v1.3 docs

---

## 🗺️ **Documentation Navigation**

### By Topic

**Getting Started:**
- START_HERE.md → QUICK_START.md → STATUS.md

**Understanding the System:**
- PROJECT_SUMMARY.md → realtime_vis_plan.md → PERFORMANCE_OPTIMIZATION_v1.3.md

**Sensor Mapping:**
- annotation/ANNOTATION_QUICKSTART.md → annotation/ANNOTATION_GUIDE.md → annotation/DATAFRAME_INDEX_ASSIGNMENT.md

**Troubleshooting:**
- KNOWN_LIMITATIONS.md → STATUS.md

**Development:**
- realtime_vis_plan.md → CHANGELOG.md

### By Role

**End User (Running the App):**
1. START_HERE.md
2. QUICK_START.md
3. KNOWN_LIMITATIONS.md

**Developer (Understanding Code):**
1. PROJECT_SUMMARY.md
2. realtime_vis_plan.md
3. STATUS.md
4. CHANGELOG.md

**Researcher (Sensor Mapping):**
1. annotation/ANNOTATION_QUICKSTART.md
2. annotation/DATAFRAME_INDEX_ASSIGNMENT.md
3. annotation/ANNOTATION_GUIDE.md

---

## 📊 **Key Information at a Glance**

### System Capabilities
- **Capture Rate:** ~200 Hz (76 Hz stable)
- **Display Rate:** 10 Hz (stable)
- **Latency:** ~145ms (95% improvement from v1.0)
- **Sensors:** 165 physical, 162 mapped to data frame
- **Frame Size:** 272 bytes (2 packets)
- **Performance:** Production-ready for real-time monitoring

### Sensor Configuration
- **Total Sensors:** 165
- **Regions:** 11 (5 fingers × 2 parts + palm)
  - Thumb: tip (12) + body (6)
  - Index: tip (12) + body (6)
  - Middle: tip (12) + body (6)
  - Ring: tip (12) + body (6)
  - Little: tip (12) + body (6)
  - Palm: 75 sensors (72 mapped)
- **Data Frame Indices:** 0-271 (sensor data at specific byte positions)

### File Locations
- **Main App:** `../realtime_glove_viz.py`
- **Annotation Tool:** `../annotate_sensors.py`
- **Index Assignment:** `../assign_dataframe_indices.py`
- **Sensor Data:** `../glove_sensor_map_with_indices.csv`

---

## 🔗 **External References**

### Hardware Documentation
- **Device Specs:** `【矩侨精密】织物电子皮肤产品规格书250630-V1.1.pdf`
- **Product:** JQ20-XL-11 (Left Hand, 162 sensing points)
- **Manufacturer:** 威海矩侨精密 (Weihai JQ Industries)

### Data Formats
- **Sensor Data:** ADC values (0-255)
- **Pressure Range:** 0~350N (requires calibration)
- **Frame Rate:** ~200 Hz raw, 10 Hz display
- **Protocol:** Binary, 921600 baud, CH340 USB

---

## 📝 **Document Maintenance**

### When to Update
- **STATUS.md** - After resolving issues or implementing features
- **CHANGELOG.md** - After every significant change
- **DOCUMENTATION_INDEX.md** - When adding/moving documentation
- **WHATS_NEW_vX.X.md** - For major version releases

### Documentation Standards
- Use clear headings and sections
- Include examples and code snippets
- Cross-reference related documents
- Keep technical details in separate docs
- Update modification dates

---

## ✅ **Documentation Checklist**

- [x] Quick start guide
- [x] Architecture documentation
- [x] Status and progress tracking
- [x] Performance optimization docs
- [x] Annotation workflow guides
- [x] Data frame index assignment
- [x] Troubleshooting guide
- [x] Change log
- [x] Archive organization
- [x] This index document

---

**Need help? Start with [START_HERE.md](START_HERE.md) or [STATUS.md](STATUS.md)**

