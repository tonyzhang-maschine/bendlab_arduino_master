# Visualizer Compatibility Fix

**Date:** October 25, 2025  
**Issue:** Exception when running `realtime_glove_viz.py` after sensor_mapping.py upgrade  
**Status:** ✅ **FIXED**

---

## Problem

After upgrading `sensor_mapping.py` to v2.0, running `realtime_glove_viz.py` resulted in this error:

```
Exception: Number of brushes does not match number of points (162 != 137)
File: hand_visualizer.py, line 156, in setup_ui
```

---

## Root Cause

The upgraded `sensor_mapping.py` now tracks **162 assigned sensors** (from the CSV file), but the visualizer should display **137 unique data frame indices**.

**Why the difference?**
- **162 sensors**: Total sensors in the glove (some share data frame indices)
- **137 unique indices**: Unique byte positions in the 272-byte frame
- **Sharing**: Finger body sensors (6 per finger) all share the same data frame index

### Example of Shared Indices
```
Data Frame Index 210 (thumb_body):
  → Sensor 89, 94, 96, 98, 103, 108 (6 sensors share this index)
```

---

## The Mismatch

**Before the fix:**

```python
# hand_visualizer.py (BROKEN)
self.num_sensors = get_sensor_count()  # Returns 162 ❌
self.sensor_positions = self._create_sensor_positions()  # Creates 162 positions
self.sensor_indices = self._get_ordered_indices()  # Returns 137 indices

# Result: 162 positions, 137 indices → MISMATCH!
```

**The visualizer tried to create:**
- 162 positions (one per sensor)
- 162 color brushes (one per position)

**But it only had:**
- 137 unique data indices to read from the frame

→ **162 brushes vs 137 data points = Exception!**

---

## The Fix

Changed `hand_visualizer.py` to use **unique data frame indices** instead of total sensor count:

```python
# hand_visualizer.py (FIXED)
self.sensor_indices = self._get_ordered_indices()  # Returns 137 indices
self.num_sensors = len(self.sensor_indices)  # Now 137 ✅
self.sensor_positions = self._create_sensor_positions()  # Creates 137 positions

# Result: 137 positions, 137 indices → MATCH!
```

### Changes Made

**File:** `hand_visualizer.py`

1. **Import change:**
   ```python
   # Old
   from sensor_mapping import SENSOR_REGIONS, get_sensor_count
   
   # New
   from sensor_mapping import SENSOR_REGIONS, get_unique_data_indices
   ```

2. **Initialization order:**
   ```python
   # Old
   self.num_sensors = get_sensor_count()  # 162
   self.sensor_positions = self._create_sensor_positions()
   self.sensor_indices = self._get_ordered_indices()
   
   # New
   self.sensor_indices = self._get_ordered_indices()  # 137 indices
   self.num_sensors = len(self.sensor_indices)  # 137
   self.sensor_positions = self._create_sensor_positions()
   ```

3. **Updated docstrings** to reflect 137 unique indices instead of 136/162

---

## Why This Makes Sense

### Visualization Logic
The visualizer displays **one dot per unique data frame index**, not per sensor:

```
Data Frame     Sensors          Visualization
Index          Mapped           Dots
─────────────────────────────────────────────
210         → 89,94,96,98,103,108  →  1 dot  
213         → [6 index sensors]    →  1 dot
22          → 10                   →  1 dot
25          → 1                    →  1 dot
...                                   ...
137 indices   162 total sensors      137 dots
```

**Why?** Because multiple sensors that share the same data frame index will always have the **same value** in any given frame. So displaying them as one dot makes sense.

---

## Verification

### Test Results

```bash
$ python test_visualizer_fix.py

✅ get_unique_data_indices() returns 137 indices
✅ Extracted 137 unique indices from SENSOR_REGIONS
✅ HandVisualizer created successfully
✅ num_sensors: 137
✅ sensor_indices: 137 indices
✅ sensor_positions: (137, 2)
✅ update_sensors() completed without error
✅ All dimensions consistent: 137 sensors

ALL TESTS PASSED!
```

### Dimension Check

| Component | Count | Status |
|-----------|-------|--------|
| num_sensors | 137 | ✅ |
| sensor_indices | 137 | ✅ |
| sensor_positions | (137, 2) | ✅ |
| colors/brushes | 137 | ✅ |

---

## Impact

### What Changed
- ✅ Visualizer now uses 137 unique data indices (correct)
- ✅ Positions, indices, and colors all match (137)
- ✅ No more exception when starting the application

### What Didn't Change
- ✅ Visualization behavior is the same
- ✅ Color mapping logic unchanged
- ✅ Update mechanism unchanged
- ✅ All features still work

### Backward Compatibility
- ✅ Still compatible with `sensor_mapping.py` v2.0
- ✅ Still uses SENSOR_REGIONS for legacy support
- ✅ No breaking changes to the API

---

## Understanding the Sensor Counts

**Three different "counts" in the system:**

1. **165 total sensors** (in CSV file)
   - All sensors in the glove hardware
   - Includes 3 unassigned sensors (no data frame index)

2. **162 assigned sensors** (get_sensor_count())
   - Sensors with valid data frame indices
   - Some share the same data frame index

3. **137 unique data indices** (get_unique_data_indices())
   - Unique byte positions in the 272-byte frame
   - What the visualizer should display

```
165 total sensors
  ↓ (filter out 3 unassigned)
162 assigned sensors
  ↓ (deduplicate shared indices)
137 unique data frame indices ← Visualizer uses this!
```

---

## Future Improvements (Optional)

If you want to visualize all 162 sensors individually:

1. Use the CSV file's X,Y coordinates from `glove_sensor_map_with_indices.csv`
2. Display all 162 sensors at their exact positions
3. Handle shared indices by giving all sensors the same value

**Example:**
```python
# Future enhancement (not implemented yet)
from sensor_mapping import SENSOR_DATA_ASSIGNED, get_data_frame_index

for _, sensor in SENSOR_DATA_ASSIGNED.iterrows():
    sensor_id = sensor['sensor_id']
    x, y = sensor['x_mm'], sensor['y_mm']
    df_index = sensor['data_frame_index']
    value = frame_data[df_index]
    plot_sensor(x, y, value)  # Plot 162 dots at exact positions
```

But for now, the 137-dot visualization works perfectly and matches the data structure.

---

## Testing

### Run the main application:
```bash
cd playground
python realtime_glove_viz.py
```

**Expected result:**
- ✅ Application starts without errors
- ✅ GUI displays with 137 sensor dots
- ✅ Real-time updates work correctly
- ✅ Colors update based on pressure values

### Run the compatibility test:
```bash
python test_visualizer_fix.py
```

**Expected result:**
```
✅ ALL TESTS PASSED!
The visualizer is now compatible with the upgraded sensor_mapping.py
```

---

## Summary

**Problem:** Mismatch between sensor count (162) and unique indices (137)  
**Cause:** Upgraded sensor_mapping.py tracks all sensors, but visualizer needs unique indices  
**Solution:** Use `len(sensor_indices)` instead of `get_sensor_count()`  
**Result:** ✅ Visualizer works perfectly with upgraded sensor_mapping.py  

---

**Status:** ✅ **FIXED AND TESTED**  
**Impact:** Zero - visualization works exactly as before  
**Compatibility:** ✅ Full compatibility with sensor_mapping.py v2.0

