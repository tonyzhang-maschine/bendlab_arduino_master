# ADC to Pressure Conversion - Implementation Summary

**Date:** October 25, 2025  
**Version:** v1.4  
**Status:** ✅ **COMPLETED**

---

## 🎯 **What Was Implemented**

Added ADC-to-pressure conversion using manufacturer-provided calibration data, with support for multiple pressure units and real-time unit switching in the GUI.

---

## ✅ **Features Added**

### 1. **Pressure Calibration Module** (`pressure_calibration.py`)
- Loads calibration data from `ADC_pressure_working_curve_JQ-160pts_sensor_array_C60510.csv`
- 171 calibration points covering ADC range 0-255
- Linear interpolation for accurate conversion
- Supports 3 pressure units:
  - **kPa** (kilopascals) - Range: 0.33 - 39.92 kPa
  - **mmHg** (millimeters of mercury) - Range: 2.5 - 299.4 mmHg
  - **N/cm²** (Newtons per square centimeter) - Range: 0.033 - 3.992 N/cm²

### 2. **GUI Unit Selector**
- Dropdown menu in Control Panel
- Real-time unit switching without restarting
- Updates all displays instantly:
  - Visualization title
  - Statistics panel
  - Colorbar labels
  - Color mapping ranges

### 3. **Real-time Pressure Display**
- **Hand Visualization**: Shows pressure values with proper color scaling
- **Statistics Panel**: Displays max/mean pressure for each region
- **Colorbar**: Shows current pressure range and unit
- **Dynamic Range Adjustment**: Automatically scales colors based on current pressure

### 4. **Format Optimization**
- **kPa**: 2 decimal places (e.g., 12.34 kPa)
- **mmHg**: 1 decimal place (e.g., 123.4 mmHg)
- **N/cm²**: 3 decimal places (e.g., 1.234 N/cm²)

---

## 📁 **Files Modified**

### New Files:
1. **`pressure_calibration.py`** - Core calibration module
   - `PressureCalibration` class
   - `adc_to_pressure()` function
   - `get_calibration()` singleton
   - Demo/test code included

### Updated Files:
2. **`realtime_glove_viz.py`**
   - Added unit selector dropdown
   - Updated statistics to show pressure values
   - Added `on_unit_changed()` handler
   - Imports calibration module

3. **`hand_visualizer.py`**
   - Converts ADC to pressure before visualization
   - Added `set_pressure_unit()` method
   - Updated colorbar labels
   - Dynamic pressure range scaling
   - Updated plot title with units

---

## 🧪 **Testing Results**

### Calibration Module Test:
```
✓ Loaded calibration data: 171 points
  ADC range: 0 - 255
  Pressure range: 0.33 - 39.92 kPa

Conversion Examples:
ADC    kPa      mmHg     N/cm²   
--------------------------------
0      0.33     2.5      0.033   
50     1.65     12.4     0.165   
100    2.99     22.5     0.299   
150    6.10     45.7     0.610   
200    15.48    116.1    1.548   
255    39.92    299.4    3.992   
```

### Integration Test:
- ✅ No linting errors
- ✅ All imports successful
- ✅ Pressure conversion working
- ✅ Unit switching functional
- ✅ GUI starts without errors

---

## 🎮 **How to Use**

### Starting the Application:
```bash
cd playground
../.venv/bin/python realtime_glove_viz.py
```

### Changing Pressure Units:
1. Look for **"Pressure Unit:"** dropdown in Control Panel
2. Select desired unit (kPa, mmHg, or N/cm2)
3. All displays update automatically

### What Updates When Unit Changes:
- ✅ Plot title (e.g., "JQ Glove Real-time Pressure Map (kPa)")
- ✅ Statistics panel (e.g., "max=12.34 mean=5.67 kPa")
- ✅ Colorbar label (e.g., "Color Scale: 0.00 - 10.00 kPa")
- ✅ Color mapping (rescales to new unit's range)

---

## 📊 **Pressure Ranges by Unit**

| Unit | Symbol | Minimum | Maximum | Typical Finger Press |
|------|--------|---------|---------|---------------------|
| **kPa** | kPa | 0.33 | 39.92 | 5-15 kPa |
| **mmHg** | mmHg | 2.5 | 299.4 | 40-120 mmHg |
| **N/cm²** | N/cm² | 0.033 | 3.992 | 0.5-1.5 N/cm² |

---

## 🔧 **Technical Details**

### Calibration Data Format:
- CSV file with 4 columns: ADC reading, N/cm², mmHg, kPa
- 171 data points (not all ADC values, interpolation fills gaps)
- Non-linear response curve (steeper at higher pressures)

### Interpolation Method:
- NumPy's `np.interp()` for linear interpolation
- Extrapolation: clamps to boundary values (0-255)
- Fast and efficient for real-time use

### Dynamic Range Adjustment:
- Uses 2.5× current max pressure for good visibility
- Minimum range: 10% of full scale
- Maximum range: full calibration range
- Prevents washed-out colors for low pressures

---

## 🐛 **Known Behaviors**

### Expected:
1. **Low pressures show bright colors**: By design! Dynamic range makes small pressures visible.
2. **Color scale changes during use**: Adaptive to current pressure range for best visibility.
3. **Zero pressure = black dots**: Correct, indicates no pressure detected.

### Notes:
- Calibration is manufacturer-provided, not user-calibrated
- Assumes linear response between calibration points
- All sensors use same calibration curve (no per-sensor calibration)

---

## 🚀 **Future Enhancements (Optional)**

### Possible Improvements:
1. **Save preference**: Remember selected unit across sessions
2. **Per-sensor calibration**: Individual calibration for each sensor
3. **Custom units**: Add psi, bar, atm, etc.
4. **Calibration UI**: GUI for recalibration
5. **Export with units**: Save data with pressure values, not just ADC

### None of these are urgent - current implementation works well!

---

## 📝 **Code Example**

### Using Calibration Module:
```python
from pressure_calibration import get_calibration
import numpy as np

# Get calibration instance
cal = get_calibration()

# Convert ADC values to pressure
adc_values = np.array([0, 100, 200, 255])
pressures_kpa = cal.adc_to_pressure(adc_values, 'kPa')
pressures_mmhg = cal.adc_to_pressure(adc_values, 'mmHg')

# Get unit information
unit_info = cal.get_unit_info('kPa')
print(unit_info['symbol'])  # "kPa"
print(unit_info['format'])  # "{:.2f}"

# Get pressure range
min_p, max_p = cal.get_pressure_range('kPa')
print(f"Range: {min_p:.2f} - {max_p:.2f} kPa")
```

---

## ✅ **Summary**

**Before:**
- Raw ADC values (0-255)
- No physical meaning
- Hard to interpret sensor readings

**After:**
- Real pressure values with units
- 3 unit options (kPa, mmHg, N/cm²)
- Easy to understand and compare
- Real-time unit switching
- Professional appearance

**Impact:** Major improvement in usability and data interpretation! 🎉

---

**Version:** v1.4  
**Status:** Production Ready  
**Next:** Ready for data recording implementation (optional)

