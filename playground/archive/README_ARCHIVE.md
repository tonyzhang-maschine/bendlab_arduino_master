# Archive - Legacy & Reference Scripts

**Purpose:** Historical scripts kept for reference. Most functionality is now integrated into `realtime_glove_viz.py`.

---

## 📦 **Archived Scripts**

### 1. `jq_glove_capture.py`
**Original Purpose:** Capture raw binary data from glove for offline analysis

**Features:**
- Connects to USB serial port
- Captures data for configurable duration
- Analyzes packet structure
- Saves to timestamped `.bin` files

**Status:** ⚠️ **Superseded** by real-time visualization app

**When to Use:**
- Need to capture data without visualization
- Debugging raw packet structure
- Creating test datasets

**Usage:**
```bash
python jq_glove_capture.py
# Output: glove_data_YYYYMMDD_HHMMSS.bin
```

---

### 2. `analyze_glove_data.py`
**Original Purpose:** Analyze captured `.bin` files and generate static visualizations

**Features:**
- Parses binary data using delimiter
- Combines packet pairs into frames
- Extracts sensor values
- Calculates statistics per region
- Generates static pressure map PNG

**Status:** ⚠️ **Superseded** by real-time visualization

**When to Use:**
- Analyzing previously captured `.bin` files
- Generating publication-quality static images
- Batch processing multiple captures

**Usage:**
```bash
python analyze_glove_data.py glove_data_20251024_214706.bin
# Output: glove_data_20251024_214706_pressure_map.png
```

---

### 3. `visualize_raw_data.py`
**Original Purpose:** Visualize raw data distribution across all 272 bytes

**Features:**
- Heatmap of all frame bytes
- Bar chart of non-zero values
- Identifies active data regions
- Helps understand data layout

**Status:** 🔧 **Debugging Tool**

**When to Use:**
- Debugging sensor mapping issues
- Understanding frame structure
- Identifying unexpected data patterns
- Verifying which bytes are active

**Usage:**
```bash
python visualize_raw_data.py glove_data_20251024_214706.bin
# Output: heatmap and bar chart visualization
```

---

### 4. `quick_data_check.py`
**Original Purpose:** Quick inspection of raw packet structure

**Features:**
- Shows delimiter count
- Displays first packet details
- Lists non-zero value positions
- Minimal processing for fast checks

**Status:** 🔧 **Debugging Tool**

**When to Use:**
- Quick validation of `.bin` file integrity
- Checking if data was captured correctly
- Debugging parser issues

**Usage:**
```bash
python quick_data_check.py glove_data_20251024_214706.bin
```

---

## 🔄 **Migration Path**

### From Legacy → Current System

| Old Script | New Equivalent | Notes |
|------------|----------------|-------|
| `jq_glove_capture.py` | `realtime_glove_viz.py` | Now has real-time display |
| `analyze_glove_data.py` | Built into main app | Live statistics panel |
| `visualize_raw_data.py` | `hand_visualizer.py` | Real-time visualization |
| `quick_data_check.py` | `test_compatibility.py` | More comprehensive tests |

### Why These Were Replaced

1. **Real-time is Better:**
   - No need to capture → analyze separately
   - Immediate feedback during testing
   - Interactive exploration

2. **Integrated Workflow:**
   - Single application for capture + visualization
   - Consistent data handling
   - Better user experience

3. **Modern Architecture:**
   - Multi-threaded (no blocking)
   - PyQtGraph (faster rendering)
   - Documented sensor mapping

---

## 📚 **Historical Context**

### Development Timeline

1. **Phase 1:** Exploration (jq_glove_capture.py, quick_data_check.py)
   - Understanding protocol
   - Capturing test data
   - Analyzing packet structure

2. **Phase 2:** Static Analysis (analyze_glove_data.py, visualize_raw_data.py)
   - Offline visualization
   - Sensor mapping experiments
   - Statistics calculation

3. **Phase 3:** Real-time System (realtime_glove_viz.py) ← **Current**
   - Live visualization
   - Threaded architecture
   - Production-ready GUI

---

## 🔧 **When to Use Legacy Scripts**

### Still Useful For:

1. **Offline Analysis**
   - Analyzing old captures
   - Batch processing multiple files
   - Creating static reports

2. **Debugging**
   - Raw packet inspection
   - Data format verification
   - Comparing different capture sessions

3. **Research**
   - Sensor calibration studies
   - Long-term data analysis
   - Publication figures

### Not Recommended For:

- ❌ Daily use (use realtime_glove_viz.py instead)
- ❌ Production deployment
- ❌ Real-time monitoring

---

## 📝 **Maintenance Status**

| Script | Maintained? | Compatible? |
|--------|-------------|-------------|
| `jq_glove_capture.py` | ✅ Yes | ✅ Should work |
| `analyze_glove_data.py` | ⚠️ Partial | 🟡 May need sensor_mapping update |
| `visualize_raw_data.py` | ✅ Yes | ✅ Should work |
| `quick_data_check.py` | ✅ Yes | ✅ Should work |

**Note:** These scripts may not use the updated `sensor_mapping.py` format. They use older sequential indexing (0-161) instead of documented indices.

---

## 🔗 **See Also**

- **[../STATUS.md](../STATUS.md)** - Current system status
- **[../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md)** - Main documentation
- **[../README.md](../README.md)** - Project overview

---

**Archived:** October 24, 2025  
**Reason:** Functionality integrated into main application  
**Preservation:** Kept for reference and debugging purposes



