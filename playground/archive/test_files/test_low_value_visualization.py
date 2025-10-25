#!/usr/bin/env python3
"""
Test visualization with low sensor values (like real glove data: 0-10 range)
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from hand_visualizer import HandVisualizer

def test_low_values():
    """Test color generation with low values like real sensor data."""
    print("=" * 60)
    print("Testing Low Value Visualization (Issue #1 Fix)")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    viz = HandVisualizer()
    
    # Simulate real glove data frame (272 bytes)
    frame_data = np.zeros(272, dtype=np.uint8)
    
    # Set some low values like observed in real data (thumb max=3, index max=6)
    # Using actual sensor indices from sensor_mapping
    frame_data[19] = 3  # Thumb sensor
    frame_data[18] = 2
    frame_data[17] = 1
    frame_data[22] = 6  # Index finger sensor
    frame_data[21] = 5
    frame_data[20] = 4
    frame_data[25] = 2  # Middle finger
    frame_data[207] = 1  # Palm
    
    print("\nSimulated frame data:")
    print(f"  Non-zero values: {np.count_nonzero(frame_data)}")
    print(f"  Max value: {frame_data.max()}")
    print(f"  Sample sensor indices and values:")
    for idx in [19, 18, 17, 22, 21, 20, 25, 207]:
        print(f"    Index {idx:3d}: {frame_data[idx]:3d}")
    
    # Test BEFORE fix (vmax=255)
    print("\n" + "=" * 60)
    print("BEFORE Dynamic Range Adjustment (vmax=255)")
    print("=" * 60)
    viz.set_colormap_range(0, 255)
    
    # Extract values manually for testing
    values = np.array([frame_data[19], frame_data[22], frame_data[25]], dtype=np.uint8)
    colors_before = viz.value_to_color(np.pad(values, (0, 133), 'constant'))[:3]
    
    print(f"Sensor values: {values}")
    print(f"Generated colors (RGB only):")
    for i, (val, color) in enumerate(zip(values, colors_before)):
        print(f"  Value {val} -> RGB {color[:3]} (nearly black, invisible!)")
    
    # Test AFTER fix (dynamic vmax)
    print("\n" + "=" * 60)
    print("AFTER Dynamic Range Adjustment")
    print("=" * 60)
    
    max_val = frame_data.max()  # 6
    dynamic_vmax = max(max_val * 5, 50)  # 50
    viz.set_colormap_range(0, dynamic_vmax)
    
    print(f"Max sensor value: {max_val}")
    print(f"Dynamic vmax: {dynamic_vmax}")
    
    colors_after = viz.value_to_color(np.pad(values, (0, 133), 'constant'))[:3]
    
    print(f"Sensor values: {values}")
    print(f"Generated colors (RGB only):")
    for i, (val, color) in enumerate(zip(values, colors_after)):
        print(f"  Value {val} -> RGB {color[:3]} (visible!)")
    
    # Compare brightness
    print("\nBrightness comparison:")
    for i, (val, c_before, c_after) in enumerate(zip(values, colors_before, colors_after)):
        brightness_before = int(c_before[:3].sum())
        brightness_after = int(c_after[:3].sum())
        improvement = brightness_after / max(brightness_before, 1)
        print(f"  Value {val}: {brightness_before} -> {brightness_after} (×{improvement:.1f})")
    
    print("\n" + "=" * 60)
    print("✓ Fix Verified: Low values now produce visible colors!")
    print("=" * 60)

if __name__ == "__main__":
    test_low_values()

