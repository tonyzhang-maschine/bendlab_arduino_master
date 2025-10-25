# JQ Glove Real-time Visualization System

## Overview
Real-time pressure visualization system for the JQ Glove (织物电子皮肤/Fabric Electronic Skin) device with multi-threaded capture and PyQtGraph-based GUI.

**Device:** JQ20-XL-11 Left Hand Glove (136 sensing points)  
**Manufacturer:** 威海矩侨精密 (Weihai JQ Industries Technology Co., Ltd)  
**Status:** 🟡 MVP Functional - Visualization colors need debugging

---

## 📖 **Quick Links**

- 🚀 **[QUICK_START.md](QUICK_START.md)** - How to run the application
- 📊 **[STATUS.md](STATUS.md)** - ⭐ **Current status and known issues**
- 📚 **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation index
- 🏗️ **[realtime_vis_plan.md](realtime_vis_plan.md)** - Architecture and design

---

## 🔌 Hardware Connection

### COM Port Information
- **Port:** `/dev/cu.usbmodem57640302171` (macOS)
- **Baudrate:** 921600 bps
- **USB Chip:** CH340 (Vendor ID: 0x1a86, Product ID: 0x55d3)
- **Connection:** Via Apple USB Hub (working fine)

---

## 📡 Protocol & Data Format

### Packet Structure
```
[Delimiter: 4 bytes] + [Packet Index: 1 byte] + [Sensor Type: 1 byte] + [Data Payload: variable]
```

**Detailed Breakdown:**
- **Delimiter:** `0xAA 0x55 0x03 0x99` (constant)
- **Packet Index:** `0x01` or `0x02` (alternating)
- **Sensor Type:** `0x06` = WB (Whole Body)
- **Data Payload:**
  - Packet `0x01`: 128 bytes (1024 bits)
  - Packet `0x02`: 144 bytes (1152 bits)

### Frame Structure
**One complete frame = 2 packets (0x01 + 0x02)**
- Total frame size: **272 bytes** (2176 bits)
- Data composition:
  - **128 bytes (packet 0x01):** Sensor data for first 128*8 = 1024 data points
  - **144 bytes (packet 0x02):** Sensor data for next 128*8 + IMU data

### Data Rate
- **Raw packet rate:** ~477 packets/second (~200 Hz actual rate)
- **Frame rate:** ~238 frames/second
- **Target visualization rate:** 10-20 Hz (sufficient for human perception)

### Data Content
Based on documentation and observation:
- **Indices 0-127 (packet 0x01):** Pressure sensor data (162 sensors distributed)
- **Indices 128-255 (packet 0x02 start):** Remaining pressure + configuration data
- **Indices 256+ (packet 0x02 end):** IMU data (accelerometer, gyroscope)
  - High values (100-250) observed at indices 256-267
  - Format: 128-byte length = sensor + config, 144-byte = sensor + config + IMU (16 bytes)

---

## 🗺️ Sensor Mapping

### Understanding the Mapping
The documentation provides **data indices** (byte positions in the 272-byte frame) for each sensor region. These are NOT sensor IDs, but rather the **actual byte offsets** where sensor data is stored.

### Glove Regions (by data index)
- **小拇指 (Little Finger):** 
  - Data indices: [31, 30, 29, 15, 14, 13, 255, 254, 253, 239, 238, 237]
  - Back sensor: [238]
  
- **无名指 (Ring Finger):** 
  - Data indices: [28, 27, 26, 12, 11, 10, 252, 251, 250, 236, 235, 234]
  - Back sensor: [219]
  
- **中指 (Middle Finger):** 
  - Data indices: [25, 24, 23, 9, 8, 7, 249, 248, 247, 233, 232, 231]
  - Back sensor: [216]
  
- **食指 (Index Finger):** 
  - Data indices: [22, 21, 20, 6, 5, 4, 246, 245, 244, 230, 229, 228]
  - Back sensor: [213]
  
- **大拇指 (Thumb):** 
  - Data indices: [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225]
  - Back sensor: [210]
  
- **手掌 (Palm):** 
  - Data indices: [207-196, 191-177, 175-161, 159-145, 143-129] (72 sensors)

**Total:** ~162 sensing points (distributed across the hand)

**✅ Confirmed:** The integers shown in the documentation diagram are direct byte positions (0-271) in the combined 272-byte frame where sensor pressure values are stored. See `sensor_mapping.py` for complete mapping.

---

## 🚀 **Running the Application**

```bash
cd playground
../.venv/bin/python realtime_glove_viz.py
```

**Expected:**
- GUI opens with hand visualization and controls
- Click "Start" to connect to glove
- Real-time statistics update at ~15 Hz
- FPS counter shows capture rate

**See [QUICK_START.md](QUICK_START.md) for detailed instructions.**

---

## 📁 **Current File Structure**

### 🎮 **Main Application**
- **`realtime_glove_viz.py`** - Main GUI application (run this!)
- **`hand_visualizer.py`** - PyQtGraph visualization widget  
- **`serial_reader.py`** - Multi-threaded serial reader
- **`glove_parser.py`** - Packet parsing and frame assembly
- **`sensor_mapping.py`** - Sensor-to-index mapping (136 sensors)

### 📚 **Documentation**
- **`STATUS.md`** - ⭐ **Current status, issues, and progress**
- **`DOCUMENTATION_INDEX.md`** - Complete documentation index
- **`QUICK_START.md`** - Quick reference guide
- **`realtime_vis_plan.md`** - Architecture and design
- **`COMPATIBILITY_UPDATE.md`** - Sensor mapping migration
- **`README_REALTIME.md`** - Original MVP documentation

### 🧪 **Testing**
- **`test_compatibility.py`** - Comprehensive system test
- **`test_app_minimal.py`** - Minimal GUI test

### 📦 **Archive**
- **`archive/`** - Legacy scripts (capture, offline analysis)
  - See `archive/README_ARCHIVE.md` for details

---

## 📊 What We Know

### ✅ Confirmed
1. Device communicates at 921600 bps via USB CDC (CH340 chip)
2. Packet delimiter is `AA 55 03 99`
3. Two packet types per frame: 0x01 (130 bytes) and 0x02 (146 bytes)
4. Frame rate is very high (~200 Hz)
5. Sensor type is consistently `0x06` (Whole Body)
6. IMU data is present in latter part of frame (indices 256-271, last 16 bytes)
7. Pressure values range from 0-255 (ADC readings)
8. **Sensor mapping is correct:** Documentation integers represent direct byte positions in 272-byte frame
   - Little finger: indices [31, 30, 29, ...] 
   - Ring finger: indices [28, 27, 26, ...]
   - Middle finger: indices [25, 24, 23, ...]
   - Index finger: indices [22, 21, 20, ...]
   - Thumb: indices [19, 18, 17, ...]
   - Palm: indices [207-129] (with gaps)
   - See `sensor_mapping.py` for complete mapping

### ⚠️ Needs Work
1. **ADC to pressure conversion:** Need calibration formula (0~350N range)
2. **IMU data parsing:** Format and units not yet decoded (16 bytes at indices 256-271)
3. **Sensor position layout:** Need accurate XY coordinates for visualization

---

## 🎯 **Current Status**

**Version:** MVP v1.0  
**Last Updated:** October 24, 2025

### ✅ **Working**
- ✅ Serial communication (921600 bps, ~200 Hz capture)
- ✅ Packet parsing and frame assembly (272 bytes)
- ✅ Real-time GUI with controls and statistics
- ✅ Per-region statistics (max, mean, active count)
- ✅ Documented sensor mapping (136 sensors)
- ✅ Start/Stop controls and connection status

### 🔴 **Known Issues** (See [STATUS.md](STATUS.md))
1. **Visualization colors not updating** - All dots remain black
2. **Sensor mapping cross-talk** - Adjacent fingers may trigger each other  
3. **Intermittent GUI freezing** - Possible data saving related

### 📊 **Performance**
- Capture: ~76 Hz (below target ~200 Hz)
- Display: 11.7 FPS (acceptable, target 15 Hz)
- Statistics: Real-time updates working correctly

### 🔧 **Next Steps**
1. Debug visualization color update (Priority: HIGH)
2. Verify sensor mapping with finger isolation tests
3. Profile GUI performance for freezing issues
4. Add data recording functionality

---

## 🔧 Dependencies

```bash
pip install numpy matplotlib pyserial
```

**Optional (for future real-time viz):**
```bash
pip install pyqtgraph PyQt5
```

---

## 📝 Notes

- The device sends data continuously at ~200 Hz
- Each frame contains 162 pressure sensor readings + IMU data
- Visualization at 10-20 Hz is sufficient for real-time display
- Need to press glove sensors and observe data changes to verify mapping
- Documentation is in Chinese but includes detailed sensor layout diagrams

---

## 🔗 References

- Documentation: `【矩侨精密】织物电子皮肤产品规格书250630-V1.1.pdf`
- Product: JQ20-XL-11 (Left Hand, 162 sensing points)
- Sensing Resolution: 271 × 161mm (±3%)
- Pressure Range: 0~350N

