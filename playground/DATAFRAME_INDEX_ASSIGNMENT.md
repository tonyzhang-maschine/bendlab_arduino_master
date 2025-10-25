# Data Frame Index Assignment

## Overview

This document explains the data frame index assignment system for mapping sensor_id to data_frame_index (byte positions in the 272-byte data frame).

## Files

- **Input:** `glove_sensor_map_annotated.csv` (sensor_id, x_mm, y_mm, region)
- **Output:** `glove_sensor_map_with_indices.csv` (+ data_frame_index column)
- **Tool:** `assign_dataframe_indices.py`

## Mapping Strategy

### Finger Bodies (Shared Indices)
All sensors in the same finger body share ONE data frame index:

| Region | Data Frame Index | Sensors |
|--------|------------------|---------|
| thumb_body | 210 | 6 sensors |
| index_body | 213 | 6 sensors |
| middle_body | 216 | 6 sensors |
| ring_body | 219 | 6 sensors |
| little_body | 222 | 6 sensors |

### Finger Tips (Unique Indices)
Each finger tip has 12 sensors arranged in 4 rows × 3 columns grid:

- **Layout:** Row-major order (left→right, top→bottom)
- **Sorting:** By Y descending (top to bottom), then X ascending (left to right)
- **Assignment:** Sequential from documentation index list

Example for thumb_tip:
```
Row 1: [19, 18, 17]
Row 2: [3, 2, 1]
Row 3: [243, 242, 241]
Row 4: [227, 226, 225]
```

### Palm (Unique Indices)
Palm sensors mapped to 72 available indices from documentation:

- **Layout:** 5 rows × 12-15 columns (irregular grid)
- **Sorting:** By Y descending, then X ascending
- **Assignment:** Sequential from row 1 to row 5

Palm indices: 207-129 (with gaps at 144, 160, 176, 192-195)

## Results

### Assignment Statistics

```
Total sensors:        165
Assigned:             162 (98.2%)
Unassigned:           3 (1.8%)
Unique DF indices:    137
DF index range:       1 - 255
```

### By Region

| Region | Assigned | Total | Status |
|--------|----------|-------|--------|
| thumb_tip | 12 | 12 | ✅ Complete |
| thumb_body | 6 | 6 | ✅ Complete |
| index_tip | 12 | 12 | ✅ Complete |
| index_body | 6 | 6 | ✅ Complete |
| middle_tip | 12 | 12 | ✅ Complete |
| middle_body | 6 | 6 | ✅ Complete |
| ring_tip | 12 | 12 | ✅ Complete |
| ring_body | 6 | 6 | ✅ Complete |
| little_tip | 12 | 12 | ✅ Complete |
| little_body | 6 | 6 | ✅ Complete |
| palm | 72 | 75 | ⚠️ 3 unassigned |

### Unassigned Sensors

Due to hardware/documentation discrepancy, 3 palm sensors remain unassigned (marked with -1):

- Sensor 163: palm at (45.7, 98.1) mm
- Sensor 164: palm at (43.0, 97.6) mm  
- Sensor 165: palm at (40.3, 97.0) mm

These are at the lowest Y coordinates (bottom of palm, near wrist).

## Usage

### Run Assignment Tool

```bash
cd playground
../.venv/bin/python assign_dataframe_indices.py
```

### Load Results

```python
import pandas as pd

# Load sensor data with data frame indices
df = pd.read_csv('glove_sensor_map_with_indices.csv')

# Filter out unassigned sensors
df_assigned = df[df['data_frame_index'] != -1]

# Get data frame index for a specific sensor
sensor_10_index = df[df['sensor_id'] == 10]['data_frame_index'].values[0]

# Get all sensors mapping to a specific data frame index
thumb_body_sensors = df[df['data_frame_index'] == 210]
```

### Using in Real-time Visualization

```python
# Read data frame (272 bytes)
frame_data = read_serial_frame()

# Get value for sensor 10
sensor_id = 10
df_index = sensor_map[sensor_id]['data_frame_index']
if df_index != -1:
    sensor_value = frame_data[df_index]
else:
    # Sensor not mapped, skip or handle
    pass
```

## Data Frame Index Layout

### Overview
- **Frame size:** 272 bytes total
- **Packet 1 (0x01):** 128 bytes (indices 0-127)
- **Packet 2 (0x02):** 144 bytes (indices 128-271)
- **IMU data:** Indices 256-271 (last 16 bytes)

### Sensor Regions in Frame

```
Indices 1-31:     Finger tips (rows 2-4)
Indices 129-207:  Palm
Indices 210-255:  Finger bodies + finger tips (row 3-4)
```

## Known Limitations

1. **Hardware discrepancy:** Glove has 75 palm sensors but documentation shows 72 indices
2. **Unassigned sensors:** 3 palm sensors (163-165) have no data frame index
3. **Manual correction needed:** May need to verify assignments with physical testing
4. **Row mismatch:** Documentation shows slightly different row/column layout than actual hardware

## Next Steps

1. **Filter unassigned sensors** in visualization code
2. **Physical validation** - Test with real glove to verify mappings
3. **Manual correction** - Adjust if certain sensors map incorrectly
4. **Update sensor_mapping.py** - Use this CSV instead of hard-coded indices

## References

- **Documentation:** `【矩侨精密】织物电子皮肤产品规格书250630-V1.1.pdf`
- **Annotation guide:** `ANNOTATION_GUIDE.md`
- **Assignment script:** `assign_dataframe_indices.py`

