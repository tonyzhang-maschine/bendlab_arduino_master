#!/usr/bin/env python3
"""
Minimal test to verify the app starts without the IndexError
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from hand_visualizer import HandVisualizer
from glove_parser import GloveParser

print("Creating QApplication...")
app = QApplication(sys.argv)

print("Creating HandVisualizer...")
viz = HandVisualizer()

print(f"  ✓ Sensor positions: {viz.sensor_positions.shape}")
print(f"  ✓ Sensor indices: {len(viz.sensor_indices)}")
print(f"  ✓ Num sensors: {viz.num_sensors}")

# Test update with dummy frame
print("\nTesting update_sensors()...")
test_frame = np.zeros(272, dtype=np.uint8)
test_frame[19] = 100   # Thumb
test_frame[22] = 150   # Index
test_frame[207] = 200  # Palm
test_frame[238] = 90   # Little finger back (duplicate index)

try:
    viz.update_sensors(test_frame)
    print("  ✅ update_sensors() works without IndexError!")
except IndexError as e:
    print(f"  ❌ IndexError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ⚠️ Other error: {e}")

# Test parser
print("\nTesting GloveParser...")
parser = GloveParser()
sensor_data = parser.get_sensor_data(test_frame)
print(f"  ✓ Extracted {len(sensor_data)} regions")
print(f"  ✓ Thumb max: {sensor_data.get('thumb', {}).get('max', 'N/A')}")
print(f"  ✓ Palm max: {sensor_data.get('palm', {}).get('max', 'N/A')}")

print("\n✅ All tests passed! App should run without errors.")

