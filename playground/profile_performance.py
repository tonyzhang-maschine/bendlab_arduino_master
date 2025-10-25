#!/usr/bin/env python3
"""
Performance profiling for Issue #3 - GUI Freezing
Identifies bottlenecks in the update pipeline
"""

import time
import numpy as np
from sensor_mapping import extract_sensor_values
from hand_visualizer import HandVisualizer
from glove_parser import GloveParser
from PyQt5.QtWidgets import QApplication
import sys

def profile_operations():
    """Profile key operations to find bottlenecks."""
    print("=" * 70)
    print("Performance Profiling - Issue #3 Investigation")
    print("=" * 70)
    
    # Create test frame data
    frame_data = np.random.randint(0, 10, size=272, dtype=np.uint8)
    
    # Setup
    app = QApplication(sys.argv)
    viz = HandVisualizer()
    parser = GloveParser()
    
    # Profile 1: extract_sensor_values (called in get_sensor_data)
    print("\n1. Testing extract_sensor_values() [CALLED EVERY FRAME]")
    iterations = 1000
    start = time.time()
    for _ in range(iterations):
        sensor_data = extract_sensor_values(frame_data)
    elapsed = (time.time() - start) * 1000
    print(f"   {iterations} iterations: {elapsed:.2f}ms")
    print(f"   Per call: {elapsed/iterations:.3f}ms")
    print(f"   At 15 Hz: {elapsed/iterations * 15:.2f}ms per GUI update")
    
    # Profile 2: HandVisualizer.update_sensors
    print("\n2. Testing HandVisualizer.update_sensors() [CALLED EVERY FRAME]")
    start = time.time()
    for _ in range(iterations):
        viz.update_sensors(frame_data)
    elapsed = (time.time() - start) * 1000
    print(f"   {iterations} iterations: {elapsed:.2f}ms")
    print(f"   Per call: {elapsed/iterations:.3f}ms")
    print(f"   At 15 Hz: {elapsed/iterations * 15:.2f}ms per GUI update")
    
    # Profile 3: Combined operation (current approach)
    print("\n3. Testing COMBINED (get_sensor_data + update_sensors)")
    print("   This is what happens in update_display() - DOUBLE EXTRACTION!")
    start = time.time()
    for _ in range(iterations):
        sensor_data = extract_sensor_values(frame_data)  # For statistics
        viz.update_sensors(frame_data)  # Extracts AGAIN for visualization
    elapsed = (time.time() - start) * 1000
    print(f"   {iterations} iterations: {elapsed:.2f}ms")
    print(f"   Per call: {elapsed/iterations:.3f}ms")
    print(f"   At 15 Hz: {elapsed/iterations * 15:.2f}ms per GUI update")
    
    # Profile 4: Breakdown of extract_sensor_values
    print("\n4. Breakdown of extract_sensor_values()")
    
    # Test just value extraction
    start = time.time()
    for _ in range(iterations):
        for region_name, region_info in [('thumb', {'data_indices': [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225]})]:
            indices = region_info['data_indices']
            values = [frame_data[idx] for idx in indices if idx < len(frame_data)]
    elapsed1 = (time.time() - start) * 1000
    
    # Test with statistics calculation
    start = time.time()
    for _ in range(iterations):
        for region_name, region_info in [('thumb', {'data_indices': [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225]})]:
            indices = region_info['data_indices']
            values = [frame_data[idx] for idx in indices if idx < len(frame_data)]
            max_val = int(max(values)) if values else 0
            mean_val = float(np.mean(values)) if values else 0.0
            active = sum(1 for v in values if v > 0)
    elapsed2 = (time.time() - start) * 1000
    
    print(f"   Just extraction (1 region × 1000): {elapsed1:.2f}ms")
    print(f"   With stats (1 region × 1000): {elapsed2:.2f}ms")
    print(f"   Stats overhead: {elapsed2 - elapsed1:.2f}ms")
    print(f"   For 11 regions: ~{(elapsed2 - elapsed1) * 11:.2f}ms total overhead")
    
    # Profile 5: Queue operations
    print("\n5. Testing Queue operations")
    from queue import Queue
    q = Queue(maxsize=50)
    
    # Fill queue
    for i in range(50):
        q.put(frame_data.copy())
    
    start = time.time()
    for _ in range(iterations):
        if not q.empty():
            try:
                data = q.get_nowait()
                q.put_nowait(data)
            except:
                pass
    elapsed = (time.time() - start) * 1000
    print(f"   Queue get/put (×1000): {elapsed:.2f}ms")
    print(f"   Per operation: {elapsed/iterations:.3f}ms (negligible)")
    
    # Summary
    print("\n" + "=" * 70)
    print("BOTTLENECK ANALYSIS")
    print("=" * 70)
    print("\nAt 15 Hz update rate (66.7ms per frame):")
    print("  - Target: < 16ms per update (for 60 FPS smooth GUI)")
    print("  - Acceptable: < 33ms per update (for 30 FPS)")
    print("  - Current budget: 66.7ms per update")
    print("\nEstimated current performance:")
    
    # Calculate totals
    extract_time = 0
    update_time = 0
    
    start = time.time()
    sensor_data = extract_sensor_values(frame_data)
    extract_time = (time.time() - start) * 1000
    
    start = time.time()
    viz.update_sensors(frame_data)
    update_time = (time.time() - start) * 1000
    
    total_time = extract_time + update_time
    
    print(f"  1. extract_sensor_values(): {extract_time:.3f}ms")
    print(f"  2. update_sensors(): {update_time:.3f}ms")
    print(f"  3. TOTAL per frame: {total_time:.3f}ms")
    print(f"  4. At 15 Hz: {total_time * 15:.2f}ms every 66.7ms")
    print(f"  5. GUI thread busy: {(total_time * 15 / 66.7 * 100):.1f}% of time")
    
    if total_time > 16:
        print(f"\n⚠️  WARNING: {total_time:.1f}ms is TOO SLOW for smooth 60 FPS GUI")
    if total_time > 33:
        print(f"\n🔴 CRITICAL: {total_time:.1f}ms will cause visible GUI freezing!")
    
    print("\nRECOMMENDATIONS:")
    print("  1. Cache extracted values to avoid double extraction")
    print("  2. Optimize extract_sensor_values() (use numpy indexing)")
    print("  3. Move heavy calculations off GUI thread if needed")
    print("  4. Consider updating statistics at lower rate than visualization")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    profile_operations()

