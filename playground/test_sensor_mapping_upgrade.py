#!/usr/bin/env python3
"""
Test script for upgraded sensor_mapping.py

Verifies:
1. CSV loading and sensor-level mapping
2. Backward compatibility with legacy region-based API
3. New sensor-level API functions
4. Shared data indices handling
5. Unassigned sensor handling
"""

import numpy as np
from sensor_mapping import (
    # New API
    get_sensor_by_id,
    get_sensors_by_region,
    get_data_frame_index,
    get_sensors_for_data_index,
    extract_all_sensor_values,
    get_region_statistics,
    get_unique_data_indices,
    # Legacy API
    extract_sensor_values,
    get_sensor_count,
    get_all_sensor_indices,
    SENSOR_DATA,
    SENSOR_DATA_ASSIGNED,
    REGION_INFO,
    SENSOR_REGIONS,
)

def test_csv_loading():
    """Test 1: CSV loading"""
    print("=" * 80)
    print("TEST 1: CSV Loading")
    print("-" * 80)
    
    assert SENSOR_DATA is not None, "CSV data should be loaded"
    assert len(SENSOR_DATA) == 165, f"Expected 165 sensors, got {len(SENSOR_DATA)}"
    assert len(SENSOR_DATA_ASSIGNED) == 162, f"Expected 162 assigned sensors, got {len(SENSOR_DATA_ASSIGNED)}"
    
    print(f"✅ CSV loaded successfully")
    print(f"   Total sensors: {len(SENSOR_DATA)}")
    print(f"   Assigned: {len(SENSOR_DATA_ASSIGNED)}")
    print(f"   Unassigned: {len(SENSOR_DATA) - len(SENSOR_DATA_ASSIGNED)}")

def test_sensor_by_id():
    """Test 2: Get sensor by ID"""
    print("\n" + "=" * 80)
    print("TEST 2: Get Sensor by ID")
    print("-" * 80)
    
    # Test valid sensor
    sensor = get_sensor_by_id(10)
    assert sensor is not None, "Sensor 10 should exist"
    assert 'sensor_id' in sensor, "Should have sensor_id field"
    assert 'x_mm' in sensor, "Should have x_mm field"
    assert 'y_mm' in sensor, "Should have y_mm field"
    assert 'region' in sensor, "Should have region field"
    assert 'data_frame_index' in sensor, "Should have data_frame_index field"
    
    print(f"✅ Sensor 10 info:")
    print(f"   Position: ({sensor['x_mm']:.1f}, {sensor['y_mm']:.1f}) mm")
    print(f"   Region: {sensor['region']}")
    print(f"   Data frame index: {sensor['data_frame_index']}")
    
    # Test invalid sensor
    sensor_invalid = get_sensor_by_id(999)
    assert sensor_invalid is None, "Sensor 999 should not exist"
    print(f"✅ Invalid sensor ID returns None correctly")

def test_sensors_by_region():
    """Test 3: Get sensors by region"""
    print("\n" + "=" * 80)
    print("TEST 3: Get Sensors by Region")
    print("-" * 80)
    
    thumb_tip_sensors = get_sensors_by_region('thumb_tip')
    assert len(thumb_tip_sensors) == 12, f"Expected 12 thumb_tip sensors, got {len(thumb_tip_sensors)}"
    
    palm_sensors = get_sensors_by_region('palm')
    assert len(palm_sensors) == 75, f"Expected 75 palm sensors, got {len(palm_sensors)}"
    
    print(f"✅ thumb_tip: {len(thumb_tip_sensors)} sensors")
    print(f"✅ palm: {len(palm_sensors)} sensors (3 unassigned)")
    
    # Count assigned vs unassigned
    palm_assigned = [s for s in palm_sensors if s['data_frame_index'] >= 0]
    palm_unassigned = [s for s in palm_sensors if s['data_frame_index'] == -1]
    print(f"   - {len(palm_assigned)} assigned")
    print(f"   - {len(palm_unassigned)} unassigned")

def test_data_frame_index():
    """Test 4: Get data frame index for sensor"""
    print("\n" + "=" * 80)
    print("TEST 4: Get Data Frame Index")
    print("-" * 80)
    
    # Test assigned sensor
    df_idx = get_data_frame_index(10)
    assert df_idx >= 0, f"Sensor 10 should have valid data frame index, got {df_idx}"
    print(f"✅ Sensor 10 → data frame index {df_idx}")
    
    # Test unassigned sensor (163, 164, or 165)
    df_idx_unassigned = get_data_frame_index(163)
    assert df_idx_unassigned == -1, f"Sensor 163 should be unassigned (-1), got {df_idx_unassigned}"
    print(f"✅ Sensor 163 → unassigned (-1)")

def test_shared_indices():
    """Test 5: Shared data indices (finger bodies)"""
    print("\n" + "=" * 80)
    print("TEST 5: Shared Data Indices")
    print("-" * 80)
    
    # Finger bodies share indices
    thumb_body_sensors = get_sensors_for_data_index(210)
    assert len(thumb_body_sensors) == 6, f"Expected 6 sensors at index 210, got {len(thumb_body_sensors)}"
    print(f"✅ Data frame index 210 (thumb_body) → {len(thumb_body_sensors)} sensors")
    print(f"   Sensor IDs: {thumb_body_sensors}")
    
    index_body_sensors = get_sensors_for_data_index(213)
    assert len(index_body_sensors) == 6, f"Expected 6 sensors at index 213, got {len(index_body_sensors)}"
    print(f"✅ Data frame index 213 (index_body) → {len(index_body_sensors)} sensors")
    
    # Finger tips have unique indices
    unique_sensors = get_sensors_for_data_index(25)  # middle_tip sensor
    assert len(unique_sensors) == 1, f"Expected 1 sensor at index 25, got {len(unique_sensors)}"
    print(f"✅ Data frame index 25 (middle_tip) → {len(unique_sensors)} sensor (unique)")

def test_extract_all_sensor_values():
    """Test 6: Extract all sensor values"""
    print("\n" + "=" * 80)
    print("TEST 6: Extract All Sensor Values")
    print("-" * 80)
    
    # Create fake frame data
    frame_data = np.random.randint(0, 10, size=272, dtype=np.uint8)
    
    sensor_values = extract_all_sensor_values(frame_data)
    assert len(sensor_values) == 162, f"Expected 162 sensor values, got {len(sensor_values)}"
    
    print(f"✅ Extracted {len(sensor_values)} sensor values")
    
    # Verify sensor 10
    sensor_10_value = sensor_values[10]
    df_idx_10 = get_data_frame_index(10)
    expected_value = frame_data[df_idx_10]
    assert sensor_10_value == expected_value, f"Sensor 10 value mismatch"
    print(f"✅ Sensor 10 value: {sensor_10_value} (from index {df_idx_10})")

def test_region_statistics():
    """Test 7: Region statistics"""
    print("\n" + "=" * 80)
    print("TEST 7: Region Statistics")
    print("-" * 80)
    
    # Create fake frame data
    frame_data = np.zeros(272, dtype=np.uint8)
    # Set some thumb_tip values
    frame_data[19] = 10
    frame_data[18] = 20
    frame_data[17] = 30
    
    stats = get_region_statistics(frame_data, 'thumb_tip')
    assert stats is not None, "Should get stats for thumb_tip"
    assert 'max' in stats, "Should have max"
    assert 'mean' in stats, "Should have mean"
    assert 'min' in stats, "Should have min"
    assert 'active_count' in stats, "Should have active_count"
    
    print(f"✅ thumb_tip statistics:")
    print(f"   Max: {stats['max']}")
    print(f"   Mean: {stats['mean']:.2f}")
    print(f"   Min: {stats['min']}")
    print(f"   Active: {stats['active_count']}/{stats['sensor_count']}")

def test_backward_compatibility():
    """Test 8: Backward compatibility with legacy API"""
    print("\n" + "=" * 80)
    print("TEST 8: Backward Compatibility")
    print("-" * 80)
    
    # Create fake frame data
    frame_data = np.random.randint(0, 10, size=272, dtype=np.uint8)
    
    # Test legacy extract_sensor_values
    sensor_values = extract_sensor_values(frame_data)
    assert 'thumb' in sensor_values, "Should have thumb region"
    assert 'palm' in sensor_values, "Should have palm region"
    
    print(f"✅ Legacy extract_sensor_values() works")
    print(f"   Regions: {list(sensor_values.keys())}")
    
    # Test legacy sensor count
    count = get_sensor_count()
    assert count == 162, f"Expected 162 sensors, got {count}"
    print(f"✅ get_sensor_count() = {count}")
    
    # Test legacy all sensor indices
    all_indices = get_all_sensor_indices()
    assert len(all_indices) > 0, "Should have sensor indices"
    print(f"✅ get_all_sensor_indices() = {len(all_indices)} unique indices")

def test_region_info():
    """Test 9: Region info structure"""
    print("\n" + "=" * 80)
    print("TEST 9: Region Info Structure")
    print("-" * 80)
    
    assert 'thumb_tip' in REGION_INFO, "Should have thumb_tip"
    assert 'palm' in REGION_INFO, "Should have palm"
    
    thumb_info = REGION_INFO['thumb_tip']
    assert 'name' in thumb_info, "Should have name"
    assert 'color' in thumb_info, "Should have color"
    assert 'parent_finger' in thumb_info, "Should have parent_finger"
    
    print(f"✅ REGION_INFO structure correct")
    print(f"   Regions: {len(REGION_INFO)}")
    print(f"   Example (thumb_tip): {thumb_info['name']} [{thumb_info['color']}]")

def test_unique_data_indices():
    """Test 10: Unique data indices"""
    print("\n" + "=" * 80)
    print("TEST 10: Unique Data Indices")
    print("-" * 80)
    
    unique_indices = get_unique_data_indices()
    assert len(unique_indices) == 137, f"Expected 137 unique indices, got {len(unique_indices)}"
    assert min(unique_indices) >= 1, "Min index should be >= 1"
    assert max(unique_indices) <= 255, "Max index should be <= 255"
    
    print(f"✅ {len(unique_indices)} unique data frame indices")
    print(f"   Range: {min(unique_indices)} - {max(unique_indices)}")

def main():
    """Run all tests"""
    print("\n" + "🧪 " * 40)
    print("SENSOR MAPPING UPGRADE TEST SUITE")
    print("🧪 " * 40 + "\n")
    
    try:
        test_csv_loading()
        test_sensor_by_id()
        test_sensors_by_region()
        test_data_frame_index()
        test_shared_indices()
        test_extract_all_sensor_values()
        test_region_statistics()
        test_backward_compatibility()
        test_region_info()
        test_unique_data_indices()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED! ✅")
        print("=" * 80)
        print("\nSummary:")
        print("  ✅ CSV loading and parsing")
        print("  ✅ Sensor-level API (new)")
        print("  ✅ Region-level API (legacy)")
        print("  ✅ Shared indices handling")
        print("  ✅ Unassigned sensor handling")
        print("  ✅ Backward compatibility")
        print("\nThe upgraded sensor_mapping.py is ready for use!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



