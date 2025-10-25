#!/usr/bin/env python3
"""
Detailed profiling to find exact bottleneck in update_sensors()
"""

import time
import numpy as np
from hand_visualizer import HandVisualizer
from PyQt5.QtWidgets import QApplication
import sys

def profile_detailed():
    """Profile each step in update_sensors() separately."""
    print("=" * 70)
    print("Detailed Profiling - Breaking down update_sensors()")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    viz = HandVisualizer()
    
    # Create test frame
    frame_data = np.random.randint(0, 10, size=272, dtype=np.uint8)
    
    iterations = 1000
    
    # Step 1: Value extraction
    print("\nStep 1: Value extraction (fancy indexing)")
    start = time.time()
    for _ in range(iterations):
        values = frame_data[viz.sensor_indices]
    elapsed = (time.time() - start) * 1000
    print(f"  {iterations} iterations: {elapsed:.2f}ms")
    print(f"  Per call: {elapsed/iterations:.3f}ms")
    
    # Step 2: Max value calculation
    print("\nStep 2: Max value calculation")
    values = frame_data[viz.sensor_indices]
    start = time.time()
    for _ in range(iterations):
        max_val = values.max()
    elapsed = (time.time() - start) * 1000
    print(f"  {iterations} iterations: {elapsed:.2f}ms")
    print(f"  Per call: {elapsed/iterations:.3f}ms")
    
    # Step 3: Dynamic range calculation
    print("\nStep 3: Dynamic range adjustment")
    start = time.time()
    for _ in range(iterations):
        max_val = values.max()
        if max_val > 0:
            dynamic_vmax = max(min(max_val * 2.5, 255), 10)
            viz.set_colormap_range(0, dynamic_vmax)
    elapsed = (time.time() - start) * 1000
    print(f"  {iterations} iterations: {elapsed:.2f}ms")
    print(f"  Per call: {elapsed/iterations:.3f}ms")
    
    # Step 4: Color conversion
    print("\nStep 4: Color conversion (value_to_color)")
    start = time.time()
    for _ in range(iterations):
        colors = viz.value_to_color(values)
    elapsed = (time.time() - start) * 1000
    print(f"  {iterations} iterations: {elapsed:.2f}ms")
    print(f"  Per call: {elapsed/iterations:.3f}ms")
    
    # Step 5: PyQtGraph setData call
    print("\nStep 5: PyQtGraph setData() [CRITICAL]")
    colors = viz.value_to_color(values)
    start = time.time()
    for _ in range(iterations):
        viz.sensor_scatter.setData(
            pos=viz.sensor_positions,
            brush=colors
        )
    elapsed = (time.time() - start) * 1000
    print(f"  {iterations} iterations: {elapsed:.2f}ms")
    print(f"  Per call: {elapsed/iterations:.3f}ms")
    print(f"  🔴 THIS IS THE BOTTLENECK!" if elapsed/iterations > 2 else "  ✅ Fast enough")
    
    # Full update_sensors() for comparison
    print("\nFull update_sensors() for comparison:")
    start = time.time()
    for _ in range(iterations):
        viz.update_sensors(frame_data)
    elapsed = (time.time() - start) * 1000
    print(f"  {iterations} iterations: {elapsed:.2f}ms")
    print(f"  Per call: {elapsed/iterations:.3f}ms")
    
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("\nTime breakdown per update_sensors() call:")
    
    # Re-measure each step
    values = frame_data[viz.sensor_indices]
    
    t_extract = 0
    start = time.time()
    for _ in range(100):
        v = frame_data[viz.sensor_indices]
    t_extract = (time.time() - start) * 1000 / 100
    
    t_range = 0
    start = time.time()
    for _ in range(100):
        m = values.max()
        d = max(min(m * 2.5, 255), 10)
    t_range = (time.time() - start) * 1000 / 100
    
    t_colors = 0
    start = time.time()
    for _ in range(100):
        c = viz.value_to_color(values)
    t_colors = (time.time() - start) * 1000 / 100
    
    t_setdata = 0
    colors = viz.value_to_color(values)
    start = time.time()
    for _ in range(100):
        viz.sensor_scatter.setData(pos=viz.sensor_positions, brush=colors)
    t_setdata = (time.time() - start) * 1000 / 100
    
    total = t_extract + t_range + t_colors + t_setdata
    
    print(f"  1. Value extraction:     {t_extract:.3f}ms ({t_extract/total*100:.1f}%)")
    print(f"  2. Range adjustment:     {t_range:.3f}ms ({t_range/total*100:.1f}%)")
    print(f"  3. Color conversion:     {t_colors:.3f}ms ({t_colors/total*100:.1f}%)")
    print(f"  4. PyQt setData():       {t_setdata:.3f}ms ({t_setdata/total*100:.1f}%)")
    print(f"  ----------------------------------------")
    print(f"  TOTAL:                   {total:.3f}ms")
    print(f"\n  At 15 Hz update rate: {total * 15:.2f}ms every 66.7ms")
    print(f"  GUI busy: {total * 15 / 66.7 * 100:.1f}%")
    
    if t_setdata > total * 0.5:
        print(f"\n🔴 BOTTLENECK: PyQt setData() takes {t_setdata/total*100:.0f}% of time!")
        print("   This is a PyQtGraph limitation, not our code.")
        print("   Solution: Reduce update frequency or cache when no changes.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    profile_detailed()

