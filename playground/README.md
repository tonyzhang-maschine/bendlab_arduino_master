# JQ Glove Real-time Visualization System

## Overview
Real-time pressure visualization system for the JQ Glove (织物电子皮肤/Fabric Electronic Skin) device with multi-threaded capture and PyQtGraph-based GUI.

**Device:** JQ20-XL-11 Left Hand Glove (136 sensing points)
**Manufacturer:** 威海矩侨精密 (Weihai JQ Industries Technology Co., Ltd)
**Status:** ✅ **v1.7 Production Ready** - High-performance 200+ Hz acquisition with multiprocessing architecture!

---

## 📖 **Quick Links**

- 🚀 **[docs/QUICK_START.md](docs/QUICK_START.md)** - How to run the application
- 📊 **[docs/STATUS.md](docs/STATUS.md)** - ⭐ **Current status and resolved issues**
- ⚠️ **[docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)** - ⭐ **Performance limitations and optimization roadmap**
- 📚 **[docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** - Complete documentation index
- 🏗️ **[docs/realtime_vis_plan.md](docs/realtime_vis_plan.md)** - Architecture and design

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

### ⚠️ **CRITICAL: Indexing Convention**
The hardware documentation uses **1-based indexing** (1-272), but Python arrays use **0-based indexing** (0-271).

**All code now correctly converts:**
```python
array_index = data_frame_index - 1  # Convert 1-based to 0-based
sensor_value = frame_data[array_index]
```

See **[docs/INDEXING_CONVENTION.md](docs/INDEXING_CONVENTION.md)** for complete explanation of this critical fix.

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

## 📁 **File Structure**

### 🎮 **Main Application**
- **`realtime_glove_viz.py`** - Main GUI application (run this!)
- **`hand_visualizer.py`** - PyQtGraph visualization widget
- **`serial_reader.py`** - Multi-threaded serial reader
- **`glove_parser.py`** - Packet parsing and frame assembly (⚠️ CRITICAL: Fixed buffer bug)
- **`sensor_mapping.py`** - Sensor-to-index mapping
- **`acquisition_process.py`** - ⭐ **NEW v1.7** High-performance multiprocessing data acquisition (200+ Hz)

### 🏷️ **Sensor Mapping Tools**
- **`annotate_sensors.py`** - Interactive region annotation tool with data_frame_index editor
- **`assign_dataframe_indices.py`** - Data frame index assignment tool
- **`glove_sensor_map_refined.csv`** - Sensor coordinates (165 sensors)
- **`glove_sensor_map_annotated.csv`** - Sensors with regions (11 regions)
- **`glove_sensor_map_annotated_w_dataframe_indices.csv`** - ⭐ **ACTIVE** Complete mapping with manually verified indices
- **`glove_sensor_map_with_indices.csv`** - Legacy mapping (deprecated)
- **`run_annotation_tool.sh`** - Quick launcher for annotation tool

### 📚 **Documentation**
- **`docs/`** - Main documentation directory
  - **`STATUS.md`** - ⭐ Current status and progress
  - **`QUICK_START.md`** - Quick reference guide
  - **`KNOWN_LIMITATIONS.md`** - Performance notes
  - **`INDEXING_CONVENTION.md`** - ⭐ **CRITICAL** Off-by-one indexing fix explanation
  - **`PERFORMANCE_ROADMAP.md`** - ⭐ 4-week performance optimization plan
  - **`PERFORMANCE_OPTIMIZATION_RESULTS.md`** - ⭐ **NEW v1.7** Complete optimization analysis (3-10 Hz → 200+ Hz)
  - **`ARCHITECTURE_COMPARISON.md`** - ⭐ **NEW v1.7** Original vs multiprocessing comparison
  - **`DOCUMENTATION_INDEX.md`** - Complete navigation
  - **`annotation/`** - Sensor mapping documentation
    - Annotation guides and workflows
    - Data frame index assignment docs
- **`archive/`** - Legacy scripts and old documentation

### 🧪 **Testing**
- **`test_compatibility.py`** - Comprehensive system test
- **`test_app_minimal.py`** - Minimal GUI test
- **`test_color_generation.py`** - Color mapping verification
- **`test_sequential_processing.py`** - Sequential processing test
- **`test_fix_integration.py`** - Integration test for fixes
- **`test_acquisition_performance.py`** - ⭐ **NEW v1.7** Multiprocessing performance validation
- **`test_parser_direct.py`** - Parser performance testing
- **`test_serial_buffering.py`** - Serial read strategy comparison
- **`test_packet_order.py`** - Hardware packet ordering verification
- **`test_timing_analysis.py`** - Detailed timing breakdown
- **`test_optimal_params.py`** - Grid search for optimal parameters

### 📦 **Archive**
- **`archive/`** - Legacy scripts (capture, offline analysis)
  - See `archive/README_ARCHIVE.md` for details
- **`archive/deprecated_docs/`** - Older documentation versions
  - `README_REALTIME.md` - Original MVP documentation
  - `COMPATIBILITY_UPDATE.md`  - Sensor mapping migration details

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

**Version:** v1.7 (High-Performance Multiprocessing!)
**Last Updated:** October 28, 2025

### 🚀 **NEW: v1.7 Features!**

**High-Performance Acquisition (v1.7):**
- ✅ **200+ Hz Data Capture** - Achieved full hardware rate (was 76 Hz)
- ✅ **Multiprocessing Architecture** - True parallelism, bypasses Python GIL
- ✅ **Optimized Serial I/O** - Fixed-size 8192-byte reads with 50ms timeout
- ✅ **Parser Bug Fix** - Fixed critical buffer management issue (3→200 bytes)
- ✅ **Systematic Optimization** - Grid search found optimal parameters
- ✅ **20-80x Performance** - Improved from 3-10 Hz to 200+ Hz
- ✅ **Process Isolation** - GUI doesn't slow acquisition

**See [docs/PERFORMANCE_OPTIMIZATION_RESULTS.md](docs/PERFORMANCE_OPTIMIZATION_RESULTS.md) and [docs/ARCHITECTURE_COMPARISON.md](docs/ARCHITECTURE_COMPARISON.md) for complete details.**

**Pressure Units (v1.4):**
- ✅ **ADC to Pressure Conversion** - Real physical units (kPa, mmHg, N/cm²)
- ✅ **Manufacturer Calibration** - 171-point calibration curve
- ✅ **Real-time Unit Switching** - Change units without restart
- ✅ **Accurate Display** - All stats and visualization in pressure units

**Modern Colormaps (v1.5):**
- ✅ **5 Scientific Colormaps** - Viridis, Plasma, Turbo, YlOrRd, Hot
- ✅ **300% Better Visibility** - See low pressure values clearly
- ✅ **Colorblind-Friendly** - Perceptually uniform options
- ✅ **Real-time Switching** - Try different colormaps instantly
- ✅ **Y-axis Flip** - Proper hand orientation

**Performance (v1.3):**
- ✅ **Visualization lag: ~150ms** (95% improvement!)
- ✅ **Display FPS: 10 Hz stable**
- ✅ **OpenGL acceleration: ENABLED**
- ✅ **Window flickering: ELIMINATED**

**See [docs/PERFORMANCE_OPTIMIZATION_v1.3.md](docs/PERFORMANCE_OPTIMIZATION_v1.3.md) for:**
- Detailed benchmarks and improvements
- Before/after performance comparison
- Implementation details
- Testing procedures

**System is NOW Production Ready for:**
- ✅ **Real-time monitoring** (~150ms latency)
- ✅ **Interactive applications**
- ✅ Data logging and recording
- ✅ Offline analysis
- ✅ Sensor validation
- ✅ Development/testing
- ✅ **Gesture recognition** (with <200ms tolerance)

**Still use with caution for:**
- ⚠️ Safety-critical real-time control (<20ms required)
- ⚠️ Ultra-low latency applications (<50ms required)

---

### ✅ **Working**
- ✅ Serial communication (921600 bps, ~200 Hz capture)
- ✅ Packet parsing and frame assembly (272 bytes)
- ✅ Real-time GUI with controls and statistics
- ✅ Per-region statistics (max, mean, active count)
- ✅ Documented sensor mapping (136 sensors)
- ✅ Start/Stop controls and connection status
- ✅ **Visualization colors with dynamic range** (Issue #1 FIXED!)
- ✅ **Sequential frame processing** (Issue #3 FIXED!)
- ✅ **Adaptive processing** - Handles high data rates without freezing
- ✅ **Performance monitoring** - Queue depth, timing, FPS tracking
- ✅ **OpenGL acceleration** - Hardware-accelerated rendering (v1.3)
- ✅ **Optimized latency** - 95% reduction in lag (v1.3)
- ✅ **Stable display rate** - 10 Hz consistent (v1.3)
- ✅ **No window flickering** - Fixed-width labels (v1.3)

### 🟡 **Minor Issues** (See [STATUS.md](STATUS.md))
1. ~~**Visualization colors not updating**~~ ✅ **FIXED** - Dynamic range adjustment implemented
2. **Sensor mapping cross-talk** - Adjacent fingers may trigger each other (minor, doesn't block usage)
3. ~~**Intermittent GUI freezing**~~ ✅ **FIXED** - Sequential processing with adaptive handling

### 📊 **Performance** (v1.3 Optimized!)
- Capture: ~76 Hz (stable)
- Display: 10 Hz (stable, consistently achieved!)
- Rendering: 5.9ms per update (OpenGL accelerated, 169 Hz capable)
- Processing: Sequential with adaptive handling (1-3 frames/tick)
- Queue management: 10 frames (132ms latency, 80% reduction from v1.2)
- **Total latency: ~145ms** (95% improvement from 3+ seconds!)
- Update time: ~15ms total (6ms render + processing)
- No frame skipping - maintains data stream sequence

### 🔧 **Next Steps**

#### ✅ **Completed - Exploration Stage**
1. ~~Debug visualization color update~~ ✅ **COMPLETED** (Priority: HIGH)
2. ~~Fix GUI freezing~~ ✅ **COMPLETED** (Priority: HIGH)
3. ~~Optimize performance~~ ✅ **COMPLETED** (v1.3 - Priority: HIGH)
4. ~~Verify sensor mapping~~ ✅ **COMPLETED** (v1.6 - Priority: HIGH)
5. ~~Performance Enhancement~~ ✅ **COMPLETED** (v1.7 - Priority: HIGH)
   - ✅ Achieved 200+ Hz data acquisition (was ~76 Hz)
   - ✅ Multiprocessing architecture implementation
   - ✅ Optimized serial reading strategy (8192-byte reads, 50ms timeout)
   - ✅ Fixed GloveParser buffer management bug
   - ✅ Systematic performance profiling and optimization

#### 🎯 **Next Stage - Production Integration**

1. **LSL Integration** (Priority: HIGH)
   - Implement Lab Streaming Layer (LSL) output
   - Enable integration with other neuroscience/HCI tools
   - Support real-time streaming for external analysis
   - Leverage existing 200 Hz acquisition infrastructure

2. **HDF5 Recording** (Priority: HIGH)
   - Implement continuous data logging to HDF5 format
   - Support chunked compression for efficient storage
   - Add session metadata and timestamps
   - Enable offline analysis workflows

3. **Code Organization & Refactoring** (Priority: MEDIUM)
   - Reorganize folder structure for better readability
   - Improve modularity and separation of concerns
   - Add comprehensive code documentation
   - Prepare codebase for LLM-assisted refactoring

4. **Additional Features** (Priority: LOW)
   - Decode IMU data format
   - Implement gesture recognition pipeline
   - Add calibration workflows

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

