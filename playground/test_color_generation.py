#!/usr/bin/env python3
"""
Test script to verify color generation in hand_visualizer.py
Tests the value_to_color() function independently
"""

import sys
import numpy as np
from hand_visualizer import HandVisualizer
from PyQt5.QtWidgets import QApplication

def test_color_generation():
    """Test the value_to_color function with various inputs."""
    print("=" * 60)
    print("Testing HandVisualizer color generation")
    print("=" * 60)
    
    # Create a QApplication (required for Qt widgets)
    app = QApplication(sys.argv)
    
    # Create visualizer
    viz = HandVisualizer()
    
    # Test 1: All zeros (should be all black)
    print("\nTest 1: All zeros")
    values = np.zeros(136, dtype=np.uint8)
    colors = viz.value_to_color(values)
    print(f"  Shape: {colors.shape}, dtype: {colors.dtype}")
    print(f"  Sample colors (first 3): {colors[:3]}")
    print(f"  All black? {np.all(colors[:, :3] == 0)}")
    
    # Test 2: All max (255) - should be yellow/bright
    print("\nTest 2: All 255 (max)")
    values = np.full(136, 255, dtype=np.uint8)
    colors = viz.value_to_color(values)
    print(f"  Sample colors (first 3): {colors[:3]}")
    print(f"  Any bright? {np.any(colors[:, :3] > 200)}")
    
    # Test 3: Mixed values (like real sensor data)
    print("\nTest 3: Mixed values (simulating real data)")
    values = np.zeros(136, dtype=np.uint8)
    values[0:5] = [3, 6, 2, 1, 4]  # Like thumb data from STATUS.md
    colors = viz.value_to_color(values)
    print(f"  Input values (first 10): {values[:10]}")
    print(f"  Output colors (first 5): {colors[:5]}")
    non_black = np.any(colors[:, :3] > 0, axis=1).sum()
    print(f"  Non-black dots: {non_black}/{len(colors)}")
    
    # Test 4: Medium value (128) - should be orange/red
    print("\nTest 4: Medium value (128)")
    values = np.full(136, 128, dtype=np.uint8)
    colors = viz.value_to_color(values)
    print(f"  Sample colors (first 3): {colors[:3]}")
    print(f"  Expected: reddish/orange colors")
    
    # Test 5: Check color progression
    print("\nTest 5: Color progression (0, 50, 100, 150, 200, 255)")
    test_values = np.array([0, 50, 100, 150, 200, 255], dtype=np.uint8)
    for val in test_values:
        values = np.full(136, val, dtype=np.uint8)
        colors = viz.value_to_color(values)
        print(f"  Value {val:3d} -> RGB: {colors[0, :3]}")
    
    print("\n" + "=" * 60)
    print("Color generation test complete!")
    print("=" * 60)
    
    # Test PyQtGraph brush parameter format
    print("\nTest 6: PyQtGraph brush format verification")
    print(f"  Colors array shape: {colors.shape}")
    print(f"  Colors array dtype: {colors.dtype}")
    print(f"  Expected: (136, 4) with dtype=uint8")
    print(f"  Format matches? {colors.shape == (136, 4) and colors.dtype == np.uint8}")

if __name__ == "__main__":
    test_color_generation()

