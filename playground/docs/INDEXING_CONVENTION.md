# Data Frame Indexing Convention

## Critical Fix: Off-by-One Index Correction

### Summary
The hardware documentation uses **1-based indexing** (1-272) for sensor data positions, but Python arrays use **0-based indexing** (0-271). We must subtract 1 when converting from `data_frame_index` to array position.

---

## The Problem

### Hardware Documentation
- Uses **1-based indexing**: positions numbered 1, 2, 3, ..., 272
- When documentation says "sensor at index 1", it means the **first byte** of sensor data

### Python Arrays
- Uses **0-based indexing**: `frame_data[0], frame_data[1], ..., frame_data[271]`
- The **first byte** is accessed as `frame_data[0]`

### The Bug
Previous code directly used `data_frame_index` as array index:
```python
sensor_value = frame_data[df_index]  # WRONG! Off by one
```

This caused all sensors to read from the **wrong byte position**, leading to strange/incorrect sensor patterns.

---

## Evidence for 1-Based Indexing

1. **Index 0 is never used**
   - Both CSVs have minimum index = 1 (not 0)
   - No sensor maps to index 0

2. **Index range is 1-255**
   - Not 0-271 as expected for 0-based array
   - Suggests first 256 bytes use 1-based numbering

3. **Strange sensor patterns observed**
   - User reported strange sensor behavior
   - Classic symptom of off-by-one error

4. **Documentation examples**
   - README shows: "Thumb: indices [19, 18, 17, 3, 2, **1**, ...]"
   - Index 1 is the lowest, not 0

---

## The Fix

### Correct Approach
```python
# Convert 1-based documentation index to 0-based Python array index
array_index = data_frame_index - 1
sensor_value = frame_data[array_index]
```

### Examples
| data_frame_index | Meaning | Array Access | Byte Position |
|------------------|---------|--------------|---------------|
| 1 | First sensor byte | `frame_data[0]` | 0 |
| 23 | 23rd sensor byte | `frame_data[22]` | 22 |
| 255 | 255th sensor byte | `frame_data[254]` | 254 |
| 256-271 | IMU data | `frame_data[255-270]` | 255-270 |

---

## Files Updated

### 1. `sensor_mapping.py`
Fixed functions:
- `extract_all_sensor_values()` - Line 289-292
- `get_region_statistics()` - Line 355-359

```python
# Before (WRONG):
sensor_values[sensor_id] = frame_data[df_index]

# After (CORRECT):
array_index = df_index - 1  # Convert 1-based to 0-based
sensor_values[sensor_id] = frame_data[array_index]
```

### 2. `hand_visualizer.py`
Fixed function:
- `update_data()` - Line 312-315

```python
# Before (WRONG):
adc_values[i] = frame_data[idx]

# After (CORRECT):
array_index = idx - 1  # Convert 1-based to 0-based
adc_values[i] = frame_data[array_index]
```

---

## Frame Structure

### Complete 272-Byte Frame
```
Python Index:  0    1    2  ...  254   255   256 ... 270   271
               |<--- Sensor Data (255 bytes) --->|<- IMU (16) ->|
Doc Index:     1    2    3  ...  255   256   257 ... 271   272
```

### Important Notes

1. **Sensor Data: Bytes 0-255 (Python) = Indices 1-256 (Docs)**
   - First 256 bytes contain pressure sensor data
   - Documentation calls these "index 1" through "index 256"
   - In Python: `frame_data[0]` through `frame_data[255]`

2. **IMU Data: Bytes 255-271 (Python) = Indices 256-272 (Docs)**
   - Last 16 bytes contain IMU data
   - Documentation calls these "index 256" through "index 272"
   - In Python: `frame_data[255]` through `frame_data[271]`

3. **Byte 0 (Python Index 0 = Doc Index 1)**
   - This byte exists and contains data
   - Not mapped to any sensor in current CSV (but it's real data!)
   - Could be reserved/unused or simply not yet assigned

---

## Testing

### Verification Script
Run `test_indexing_offset.py` to see the difference between old and new approaches:

```bash
python3 test_indexing_offset.py
```

### Hardware Test
With the fix applied:
1. Launch the real-time visualizer
2. Press specific fingers on the glove
3. Verify that the **correct regions** light up in the visualization
4. The sensor patterns should now match physical finger positions

**Before Fix:** Strange patterns, wrong regions lighting up
**After Fix:** Accurate patterns matching actual finger pressure

---

## CSV Format

The `glove_sensor_map_annotated_w_dataframe_indices.csv` contains:
- `sensor_id`: Unique sensor identifier (1-165)
- `x_mm`, `y_mm`: Physical position on glove in millimeters
- `region`: Anatomical region (thumb_tip, palm, etc.)
- `data_frame_index`: **1-based** byte position in documentation (1-272)

**Always subtract 1** before using `data_frame_index` as Python array index!

---

## Summary

✅ **Always use:** `frame_data[data_frame_index - 1]`
❌ **Never use:** `frame_data[data_frame_index]` (off by one!)

This fix resolves the strange sensor patterns and ensures accurate sensor-to-data mapping.

---

**Date:** 2025-10-28
**Issue:** Off-by-one indexing error causing incorrect sensor readings
**Solution:** Convert 1-based documentation indices to 0-based Python array indices
**Impact:** Critical fix - affects all sensor data reading
