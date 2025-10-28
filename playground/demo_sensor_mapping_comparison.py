#!/usr/bin/env python3
"""
Demo: Sensor Mapping v1.0 (Legacy) vs v2.0 (Upgraded)

Shows side-by-side comparison of old and new APIs
"""

import numpy as np
from sensor_mapping import (
    # Legacy API (v1.0)
    extract_sensor_values,
    get_sensor_count,
    SENSOR_REGIONS,
    # New API (v2.0)
    get_sensor_by_id,
    get_sensors_by_region,
    extract_all_sensor_values,
    get_region_statistics,
    get_sensors_for_data_index,
)

def print_header(text):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def demo_legacy_api():
    """Demo: Legacy API (v1.0)"""
    print_header("LEGACY API (v1.0) - Region-Based")
    
    # Create fake frame data
    frame_data = np.random.randint(0, 20, size=272, dtype=np.uint8)
    
    # Extract values (region-based)
    print("\n1. Extract sensor values (region-based):")
    sensor_values = extract_sensor_values(frame_data)
    
    print(f"   Available regions: {list(sensor_values.keys())}")
    print(f"\n   Example - Thumb region:")
    print(f"     Max value: {sensor_values['thumb']['max']}")
    print(f"     Mean value: {sensor_values['thumb']['mean']:.1f}")
    print(f"     Active sensors: {sensor_values['thumb']['active_count']}")
    print(f"     Data indices: {len(sensor_values['thumb']['indices'])} indices")
    
    print(f"\n   ⚠️  Limitations:")
    print(f"     - Can't identify WHICH specific sensor has max value")
    print(f"     - No position information (x, y coordinates)")
    print(f"     - Combines tip + body sensors")
    
    # Get sensor count
    print(f"\n2. Get sensor count:")
    count = get_sensor_count()
    print(f"   Total sensors: {count}")
    
    # Show regions structure
    print(f"\n3. Available regions:")
    for region_name, region_info in SENSOR_REGIONS.items():
        print(f"   {region_info['name']:30s} - {len(region_info['data_indices'])} indices")

def demo_new_api():
    """Demo: New API (v2.0)"""
    print_header("NEW API (v2.0) - Sensor-Level + CSV-Based")
    
    # Create fake frame data (same as legacy demo)
    frame_data = np.random.randint(0, 20, size=272, dtype=np.uint8)
    
    # Extract ALL sensor values
    print("\n1. Extract ALL sensor values (sensor-level):")
    sensor_values = extract_all_sensor_values(frame_data)
    print(f"   Got {len(sensor_values)} individual sensor values")
    print(f"   Example values: {{sensor_id: value}}")
    print(f"     {dict(list(sensor_values.items())[:5])}  ...")
    
    # Find max sensor
    max_sensor_id = max(sensor_values, key=sensor_values.get)
    max_value = sensor_values[max_sensor_id]
    
    print(f"\n   ✅ Can now identify WHICH sensor has max value!")
    print(f"     Sensor ID: {max_sensor_id}")
    print(f"     Value: {max_value}")
    
    # Get sensor details
    print(f"\n2. Get detailed sensor information:")
    sensor = get_sensor_by_id(max_sensor_id)
    print(f"   Sensor {max_sensor_id}:")
    print(f"     Region: {sensor['region']}")
    print(f"     Position: ({sensor['x_mm']:.1f}, {sensor['y_mm']:.1f}) mm")
    print(f"     Data frame index: {sensor['data_frame_index']}")
    
    print(f"\n   ✅ Now have position data for visualization!")
    
    # Region-level statistics (still available)
    print(f"\n3. Region statistics (enhanced):")
    thumb_stats = get_region_statistics(frame_data, 'thumb_tip')
    print(f"   Thumb tip:")
    print(f"     Max: {thumb_stats['max']}")
    print(f"     Mean: {thumb_stats['mean']:.1f}")
    print(f"     Active: {thumb_stats['active_count']}/{thumb_stats['sensor_count']}")
    
    # Get all sensors in region
    print(f"\n4. Get all sensors in a region:")
    thumb_sensors = get_sensors_by_region('thumb_tip')
    print(f"   Thumb tip has {len(thumb_sensors)} sensors:")
    for sensor in thumb_sensors[:3]:
        sid = sensor['sensor_id']
        val = sensor_values[sid]
        print(f"     Sensor {sid:3d}: value={val:2d}, index={sensor['data_frame_index']:3d}")
    print(f"     ... and {len(thumb_sensors)-3} more")
    
    # Shared indices
    print(f"\n5. Shared data indices (NEW!):")
    thumb_body_sensors = get_sensors_for_data_index(210)
    print(f"   Data index 210 (thumb_body) is shared by {len(thumb_body_sensors)} sensors:")
    print(f"   Sensor IDs: {thumb_body_sensors}")
    print(f"\n   ✅ Properly handles hardware limitation!")

def demo_use_case_comparison():
    """Demo: Real-world use case comparison"""
    print_header("USE CASE: Find Active Sensors and Their Positions")
    
    # Create fake frame with some active sensors
    frame_data = np.zeros(272, dtype=np.uint8)
    frame_data[22] = 45  # index_tip
    frame_data[25] = 30  # middle_tip
    frame_data[19] = 20  # thumb_tip
    
    # LEGACY APPROACH
    print("\n📊 LEGACY API (v1.0):")
    print("   Code:")
    print("     sensor_values = extract_sensor_values(frame_data)")
    print("     for region, info in sensor_values.items():")
    print("         if info['max'] > 10:")
    print("             print(f'{region}: max={info[\"max\"]}')")
    print("\n   Output:")
    sensor_values_legacy = extract_sensor_values(frame_data)
    for region, info in sensor_values_legacy.items():
        if info['max'] > 10:
            print(f"     {region}: max={info['max']}")
    
    print("\n   ⚠️  Problem: Don't know WHICH sensor or WHERE it is!")
    
    # NEW APPROACH
    print("\n✨ NEW API (v2.0):")
    print("   Code:")
    print("     sensor_values = extract_all_sensor_values(frame_data)")
    print("     for sensor_id, value in sensor_values.items():")
    print("         if value > 10:")
    print("             sensor = get_sensor_by_id(sensor_id)")
    print("             print(f'Sensor {sensor_id}: {sensor[\"region\"]} at ({sensor[\"x_mm\"]:.1f}, {sensor[\"y_mm\"]:.1f}), value={value}')")
    print("\n   Output:")
    sensor_values_new = extract_all_sensor_values(frame_data)
    for sensor_id, value in sensor_values_new.items():
        if value > 10:
            sensor = get_sensor_by_id(sensor_id)
            print(f"     Sensor {sensor_id}: {sensor['region']} at ({sensor['x_mm']:.1f}, {sensor['y_mm']:.1f}) mm, value={value}")
    
    print("\n   ✅ Now know WHICH sensor AND its exact position!")

def demo_visualization_potential():
    """Demo: Visualization potential"""
    print_header("VISUALIZATION POTENTIAL")
    
    print("\n📊 LEGACY API (v1.0):")
    print("   - Can only show region-level aggregates")
    print("   - No sensor positions → can't plot accurately")
    print("   - Example: 'Thumb region has max value 45'")
    
    print("\n✨ NEW API (v2.0):")
    print("   - Can show individual sensor values")
    print("   - Has exact X,Y positions → accurate plotting")
    print("   - Example code:")
    print("     ```python")
    print("     import matplotlib.pyplot as plt")
    print("     for sensor_id, value in sensor_values.items():")
    print("         sensor = get_sensor_by_id(sensor_id)")
    print("         plt.scatter(sensor['x_mm'], sensor['y_mm'], ")
    print("                     s=value*10, c=value, cmap='hot')")
    print("     plt.colorbar()")
    print("     plt.show()")
    print("     ```")
    print("   - Result: Accurate pressure map with sensor positions!")

def main():
    """Run all demos"""
    print("\n" + "🎯 " * 40)
    print("SENSOR MAPPING: v1.0 (Legacy) vs v2.0 (Upgraded)")
    print("🎯 " * 40)
    
    demo_legacy_api()
    demo_new_api()
    demo_use_case_comparison()
    demo_visualization_potential()
    
    print_header("SUMMARY")
    print("\n✅ UPGRADE BENEFITS:")
    print("   1. Individual sensor identification and tracking")
    print("   2. Position data (x, y coordinates) for accurate visualization")
    print("   3. Proper handling of shared data indices")
    print("   4. Graceful handling of unassigned sensors")
    print("   5. CSV-based (easy to update/maintain)")
    print("   6. 100% backward compatible - legacy API still works!")
    
    print("\n📚 DOCUMENTATION:")
    print("   - Full API reference: docs/SENSOR_MAPPING_UPGRADE.md")
    print("   - Test suite: test_sensor_mapping_upgrade.py")
    print("   - Summary: SENSOR_MAPPING_V2_SUMMARY.md")
    
    print("\n✨ READY TO USE!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()


