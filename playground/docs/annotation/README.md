# Sensor Mapping Documentation

Complete documentation for the sensor annotation and data frame index assignment workflow.

---

## 📚 **Documents in This Directory**

### Quick Start
- **[ANNOTATION_QUICKSTART.md](ANNOTATION_QUICKSTART.md)** - 5-minute guide to get started
  - How to run the annotation tool
  - Step-by-step workflow
  - Expected results

### Detailed Guides  
- **[ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md)** - Complete annotation workflow
  - Selection modes (Rectangle, Lasso, Click)
  - Region assignment strategies
  - Troubleshooting tips
  
- **[ANNOTATION_TOOL_SUMMARY.md](ANNOTATION_TOOL_SUMMARY.md)** - Technical overview
  - Architecture and features
  - Code structure
  - Future enhancements

### Data Frame Index Assignment
- **[DATAFRAME_INDEX_ASSIGNMENT.md](DATAFRAME_INDEX_ASSIGNMENT.md)** - Complete mapping guide
  - How sensor_id maps to data_frame_index
  - Finger tips, bodies, and palm strategy
  - Usage in real-time visualization
  - Known limitations and solutions

---

## 🎯 **Workflow Overview**

### Step 1: Annotate Regions
Use `annotate_sensors.py` to label sensors by region:

```bash
cd playground
./run_annotation_tool.sh
```

**Input:** `glove_sensor_map_refined.csv` (165 sensors with coordinates)  
**Output:** `glove_sensor_map_annotated.csv` (sensors with 11 regions)

**Regions:**
- Thumb: tip + body
- Index: tip + body  
- Middle: tip + body
- Ring: tip + body
- Little: tip + body
- Palm

### Step 2: Assign Data Frame Indices
Use `assign_dataframe_indices.py` to map to byte positions:

```bash
cd playground
../.venv/bin/python assign_dataframe_indices.py
```

**Input:** `glove_sensor_map_annotated.csv`  
**Output:** `glove_sensor_map_with_indices.csv`

**Mapping:**
- Finger bodies → shared indices (210, 213, 216, 219, 222)
- Finger tips → unique indices (4×3 grid per finger)
- Palm → 72 unique indices (row-major sorted)

### Step 3: Use in Visualization
Load the final CSV in your visualization code:

```python
import pandas as pd

sensor_map = pd.read_csv('glove_sensor_map_with_indices.csv')
assigned_sensors = sensor_map[sensor_map['data_frame_index'] != -1]

# Read frame data
frame_data = read_serial_frame()  # 272 bytes

# Get value for a specific sensor
sensor_id = 10
df_index = sensor_map[sensor_map['sensor_id'] == sensor_id]['data_frame_index'].values[0]
if df_index != -1:
    sensor_value = frame_data[df_index]
```

---

## 📊 **Results**

- **165 sensors total**
- **162 sensors mapped** (98.2%)
- **3 sensors unassigned** (hardware exceeds documentation)
- **11 regions** (5 fingers × 2 parts + palm)
- **137 unique data frame indices**

---

## 🔗 **Related Files**

### Tools (in `playground/`)
- `annotate_sensors.py` - Interactive annotation GUI
- `assign_dataframe_indices.py` - Index assignment automation
- `run_annotation_tool.sh` - Quick launcher

### Data Files (in `playground/`)
- `glove_sensor_map_refined.csv` - Raw coordinates
- `glove_sensor_map_annotated.csv` - With regions
- `glove_sensor_map_with_indices.csv` - Complete mapping

---

## 📖 **Reading Order**

**For annotation:**
1. ANNOTATION_QUICKSTART.md (5 min)
2. ANNOTATION_GUIDE.md (full details)

**For understanding the mapping:**
1. DATAFRAME_INDEX_ASSIGNMENT.md (complete guide)

**For technical details:**
1. ANNOTATION_TOOL_SUMMARY.md (architecture)

---

## ❓ **FAQ**

**Q: Why 11 regions instead of 6?**  
A: Separating tips from bodies allows better data frame index assignment. Tips have unique indices (12 per finger), bodies share indices (6 per finger, 1 shared index).

**Q: Why are 3 sensors unassigned?**  
A: Hardware has 75 palm sensors but documentation only specifies 72 palm indices. The extra 3 sensors exceed available indices.

**Q: Can I re-annotate?**  
A: Yes! The annotation tool can load existing annotations and modify them. Just load the annotated CSV and make changes.

**Q: How do I verify the mapping is correct?**  
A: Test with the real glove - press each finger and verify the correct sensors light up in the visualization.

---

**Start here:** [ANNOTATION_QUICKSTART.md](ANNOTATION_QUICKSTART.md)


