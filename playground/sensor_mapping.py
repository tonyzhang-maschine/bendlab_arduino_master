#!/usr/bin/env python3
"""
Sensor-to-index mapping for JQ Glove (Left Hand)
Based on documentation diagram showing actual byte positions in 272-byte frame

The numbers in the documentation diagram represent DIRECT byte indices 
in the combined frame (packet 0x01 + packet 0x02 = 272 bytes)

This module provides both:
1. Sensor-level mapping: sensor_id → data_frame_index (from CSV)
2. Region-level mapping: region → data_indices (for statistics)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Get the directory where this script is located
_SCRIPT_DIR = Path(__file__).parent

# Load sensor mapping from CSV
# Updated to use the manually annotated data frame indices
_SENSOR_MAP_CSV = _SCRIPT_DIR / "glove_sensor_map_annotated_w_dataframe_indices.csv"

def _load_sensor_mapping() -> pd.DataFrame:
    """Load sensor mapping from CSV file"""
    if not _SENSOR_MAP_CSV.exists():
        raise FileNotFoundError(
            f"Sensor mapping CSV not found: {_SENSOR_MAP_CSV}\n"
            f"Please ensure glove_sensor_map_with_indices.csv exists in {_SCRIPT_DIR}"
        )
    return pd.read_csv(_SENSOR_MAP_CSV)

# Load sensor data
try:
    SENSOR_DATA = _load_sensor_mapping()
    # Filter out unassigned sensors (data_frame_index == -1)
    SENSOR_DATA_ASSIGNED = SENSOR_DATA[SENSOR_DATA['data_frame_index'] != -1].copy()
except Exception as e:
    print(f"Warning: Could not load sensor mapping CSV: {e}")
    print("Falling back to basic region-based mapping only")
    SENSOR_DATA = None
    SENSOR_DATA_ASSIGNED = None

# Region definitions with color mapping and Chinese names
REGION_INFO = {
    'thumb_tip': {
        'name': '大拇指尖 (Thumb Tip)',
        'color': 'red',
        'parent_finger': 'thumb'
    },
    'thumb_body': {
        'name': '大拇指 (Thumb)',
        'color': 'red',
        'parent_finger': 'thumb'
    },
    'index_tip': {
        'name': '食指尖 (Index Tip)',
        'color': 'orange',
        'parent_finger': 'index'
    },
    'index_body': {
        'name': '食指 (Index)',
        'color': 'orange',
        'parent_finger': 'index'
    },
    'middle_tip': {
        'name': '中指尖 (Middle Tip)',
        'color': 'green',
        'parent_finger': 'middle'
    },
    'middle_body': {
        'name': '中指 (Middle)',
        'color': 'green',
        'parent_finger': 'middle'
    },
    'ring_tip': {
        'name': '无名指尖 (Ring Tip)',
        'color': 'blue',
        'parent_finger': 'ring'
    },
    'ring_body': {
        'name': '无名指 (Ring)',
        'color': 'blue',
        'parent_finger': 'ring'
    },
    'little_tip': {
        'name': '小拇指尖 (Little Tip)',
        'color': 'purple',
        'parent_finger': 'little'
    },
    'little_body': {
        'name': '小拇指 (Little)',
        'color': 'purple',
        'parent_finger': 'little'
    },
    'palm': {
        'name': '手掌 (Palm)',
        'color': 'cyan',
        'parent_finger': None
    }
}

# Legacy region mapping (backward compatibility)
# NOTE: This uses the old region names and combines tip+body for each finger
SENSOR_REGIONS = {
    'little_finger': {
        'name': '小拇指 (Little Finger)',
        'color': 'purple',
        'data_indices': [31, 30, 29, 15, 14, 13, 255, 254, 253, 239, 238, 237, 222]  # tip + body
    },
    'ring_finger': {
        'name': '无名指 (Ring Finger)', 
        'color': 'blue',
        'data_indices': [28, 27, 26, 12, 11, 10, 252, 251, 250, 236, 235, 234, 219]  # tip + body
    },
    'middle_finger': {
        'name': '中指 (Middle Finger)',
        'color': 'green', 
        'data_indices': [25, 24, 23, 9, 8, 7, 249, 248, 247, 233, 232, 231, 216]  # tip + body
    },
    'index_finger': {
        'name': '食指 (Index Finger)',
        'color': 'orange',
        'data_indices': [22, 21, 20, 6, 5, 4, 246, 245, 244, 230, 229, 228, 213]  # tip + body
    },
    'thumb': {
        'name': '大拇指 (Thumb)',
        'color': 'red',
        'data_indices': [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225, 210]  # tip + body
    },
    'palm': {
        'name': '手掌 (Palm)',
        'color': 'cyan',
        'data_indices': [
            207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196,
            191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177,
            175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161,
            159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145,
            143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129
        ]
    }
}

# IMU data region (accelerometer, gyroscope)
# Located at the end of packet 0x02 (frame indices 256-271)
IMU_REGION = {
    'name': 'IMU (Accelerometer/Gyroscope)',
    'data_indices': list(range(256, 272))  # Last 16 bytes of frame
}

def get_all_sensor_indices():
    """Get all sensor data indices as a flat list (legacy function)"""
    all_indices = []
    for region in SENSOR_REGIONS.values():
        all_indices.extend(region['data_indices'])
    return sorted(set(all_indices))

def get_sensor_count():
    """Get total number of unique sensors"""
    if SENSOR_DATA_ASSIGNED is not None:
        return len(SENSOR_DATA_ASSIGNED)
    return len(get_all_sensor_indices())

def get_sensor_by_id(sensor_id: int) -> Optional[Dict]:
    """
    Get sensor information by sensor_id
    
    Args:
        sensor_id: Sensor ID (1-165)
    
    Returns:
        dict with keys: sensor_id, x_mm, y_mm, region, data_frame_index
        or None if not found
    """
    if SENSOR_DATA is None:
        return None
    
    row = SENSOR_DATA[SENSOR_DATA['sensor_id'] == sensor_id]
    if row.empty:
        return None
    
    return row.iloc[0].to_dict()

def get_sensors_by_region(region: str) -> List[Dict]:
    """
    Get all sensors in a specific region
    
    Args:
        region: Region name (e.g., 'thumb_tip', 'palm', 'index_body')
    
    Returns:
        List of sensor dicts, empty list if region not found
    """
    if SENSOR_DATA is None:
        return []
    
    rows = SENSOR_DATA[SENSOR_DATA['region'] == region]
    return rows.to_dict('records')

def get_data_frame_index(sensor_id: int) -> int:
    """
    Get data frame index for a sensor_id
    
    Args:
        sensor_id: Sensor ID (1-165)
    
    Returns:
        Data frame index (0-271), or -1 if sensor is unassigned/not found
    """
    sensor = get_sensor_by_id(sensor_id)
    if sensor is None:
        return -1
    return int(sensor['data_frame_index'])

def get_sensors_for_data_index(data_index: int) -> List[int]:
    """
    Get all sensor IDs that map to a specific data frame index
    (Multiple sensors can share the same index, e.g., finger bodies)
    
    Args:
        data_index: Data frame index (0-271)
    
    Returns:
        List of sensor_ids that map to this index
    """
    if SENSOR_DATA_ASSIGNED is None:
        return []
    
    rows = SENSOR_DATA_ASSIGNED[SENSOR_DATA_ASSIGNED['data_frame_index'] == data_index]
    return rows['sensor_id'].tolist()

def extract_sensor_values(frame_data):
    """
    Extract sensor values from a 272-byte frame (legacy function)
    
    Args:
        frame_data: List or bytes of length 272 (combined packet 0x01 + 0x02)
    
    Returns:
        dict: {region_name: {'indices': [...], 'values': [...], 'color': '...'}}
    """
    if len(frame_data) < 272:
        raise ValueError(f"Frame data must be 272 bytes, got {len(frame_data)}")
    
    sensor_values = {}
    
    for region_name, region_info in SENSOR_REGIONS.items():
        indices = region_info['data_indices']
        values = [frame_data[idx] for idx in indices if idx < len(frame_data)]
        
        sensor_values[region_name] = {
            'name': region_info['name'],
            'indices': indices,
            'values': values,
            'color': region_info['color'],
            'max': int(max(values)) if values else 0,
            'mean': float(np.mean(values)) if values else 0.0,
            'active_count': sum(1 for v in values if v > 0)
        }
    
    return sensor_values

def extract_all_sensor_values(frame_data) -> Dict[int, int]:
    """
    Extract values for all sensors using CSV mapping

    Args:
        frame_data: List or bytes of length 272

    Returns:
        dict: {sensor_id: value} for all assigned sensors

    Note:
        data_frame_index in CSV uses 1-based indexing (1-272)
        We convert to 0-based Python array indexing by subtracting 1
    """
    if len(frame_data) < 272:
        raise ValueError(f"Frame data must be 272 bytes, got {len(frame_data)}")

    if SENSOR_DATA_ASSIGNED is None:
        return {}

    sensor_values = {}
    for _, sensor in SENSOR_DATA_ASSIGNED.iterrows():
        sensor_id = int(sensor['sensor_id'])
        df_index = int(sensor['data_frame_index'])
        # Convert 1-based df_index to 0-based array index
        array_index = df_index - 1
        if array_index >= 0 and array_index < len(frame_data):
            sensor_values[sensor_id] = frame_data[array_index]

    return sensor_values

def extract_imu_data(frame_data):
    """
    Extract IMU data from frame
    
    Args:
        frame_data: List or bytes of length 272
        
    Returns:
        list: 16 bytes of IMU data
    """
    if len(frame_data) < 272:
        return []
    
    return [frame_data[idx] for idx in IMU_REGION['data_indices']]

def get_region_for_index(data_index):
    """
    Find which region a data index belongs to (legacy function)
    
    Args:
        data_index: Byte position in frame (0-271)
        
    Returns:
        tuple: (region_name, region_info) or (None, None) if not found
    """
    for region_name, region_info in SENSOR_REGIONS.items():
        if data_index in region_info['data_indices']:
            return region_name, region_info
    
    if data_index in IMU_REGION['data_indices']:
        return 'imu', IMU_REGION
    
    return None, None

def get_region_statistics(frame_data, region: str) -> Optional[Dict]:
    """
    Get statistics for all sensors in a region

    Args:
        frame_data: 272-byte frame
        region: Region name (e.g., 'thumb_tip', 'palm')

    Returns:
        dict with keys: max, mean, min, active_count, sensor_count
        or None if region not found or no data

    Note:
        data_frame_index in CSV uses 1-based indexing (1-272)
        We convert to 0-based Python array indexing by subtracting 1
    """
    if SENSOR_DATA_ASSIGNED is None:
        return None

    sensors = get_sensors_by_region(region)
    if not sensors:
        return None

    values = []
    for sensor in sensors:
        df_index = int(sensor['data_frame_index'])
        # Convert 1-based df_index to 0-based array index
        array_index = df_index - 1
        if array_index >= 0 and array_index < len(frame_data):
            values.append(frame_data[array_index])

    if not values:
        return None

    return {
        'max': int(max(values)),
        'min': int(min(values)),
        'mean': float(np.mean(values)),
        'active_count': sum(1 for v in values if v > 0),
        'sensor_count': len(values)
    }

def get_unique_data_indices() -> List[int]:
    """
    Get list of unique data frame indices used by sensors
    
    Returns:
        Sorted list of unique data frame indices
    """
    if SENSOR_DATA_ASSIGNED is None:
        return get_all_sensor_indices()
    
    return sorted(SENSOR_DATA_ASSIGNED['data_frame_index'].unique().tolist())

# Summary information
TOTAL_SENSORS = get_sensor_count()
FRAME_SIZE = 272  # bytes (packet 0x01: 128 + packet 0x02: 144)

if __name__ == "__main__":
    print("JQ Glove Sensor Mapping")
    print("=" * 80)
    
    # CSV-based mapping information
    if SENSOR_DATA is not None:
        print(f"\n✅ CSV Mapping Loaded: {_SENSOR_MAP_CSV.name}")
        print(f"   Total sensors: {len(SENSOR_DATA)}")
        print(f"   Assigned sensors: {len(SENSOR_DATA_ASSIGNED)} (with data_frame_index >= 0)")
        print(f"   Unassigned sensors: {len(SENSOR_DATA) - len(SENSOR_DATA_ASSIGNED)}")
        
        print("\n📍 Sensors by Region:")
        for region_name, region_info in REGION_INFO.items():
            sensors = get_sensors_by_region(region_name)
            assigned = [s for s in sensors if s['data_frame_index'] >= 0]
            color = region_info['color']
            print(f"  {region_info['name']:30s} [{color:8s}] "
                  f"{len(assigned):2d}/{len(sensors):2d} assigned")
        
        print("\n📊 Data Frame Index Coverage:")
        unique_indices = get_unique_data_indices()
        print(f"   Unique data indices used: {len(unique_indices)}")
        print(f"   Index range: {min(unique_indices)} - {max(unique_indices)}")
        
        # Show shared indices (multiple sensors → one index)
        shared_indices = []
        for df_idx in unique_indices:
            sensor_ids = get_sensors_for_data_index(df_idx)
            if len(sensor_ids) > 1:
                shared_indices.append((df_idx, sensor_ids))
        
        if shared_indices:
            print(f"\n🔗 Shared Data Indices ({len(shared_indices)} indices):")
            print("   (Multiple sensors mapping to same data frame index)")
            for df_idx, sensor_ids in shared_indices[:5]:  # Show first 5
                region = SENSOR_DATA_ASSIGNED[
                    SENSOR_DATA_ASSIGNED['data_frame_index'] == df_idx
                ]['region'].iloc[0]
                print(f"   Index {df_idx:3d}: {len(sensor_ids):2d} sensors ({region})")
            if len(shared_indices) > 5:
                print(f"   ... and {len(shared_indices) - 5} more")
        
        # Show unassigned sensors
        unassigned = SENSOR_DATA[SENSOR_DATA['data_frame_index'] == -1]
        if len(unassigned) > 0:
            print(f"\n⚠️  Unassigned Sensors ({len(unassigned)} sensors):")
            for _, sensor in unassigned.iterrows():
                print(f"   Sensor {int(sensor['sensor_id']):3d}: "
                      f"{sensor['region']:15s} at ({sensor['x_mm']:.1f}, {sensor['y_mm']:.1f}) mm")
    else:
        print("\n⚠️  CSV mapping not loaded - using legacy region-based mapping only")
    
    # Legacy region mapping information
    print("\n" + "=" * 80)
    print("Legacy Region-Based Mapping (for backward compatibility):")
    print(f"\nFrame size: {FRAME_SIZE} bytes")
    print(f"Total unique data indices: {len(get_all_sensor_indices())}")
    
    print(f"\nRegions (combined tip + body):")
    for region_name, region_info in SENSOR_REGIONS.items():
        indices = region_info['data_indices']
        print(f"  {region_info['name']:30s} {len(indices):3d} indices")
        print(f"    Indices: {indices[:5]}{'...' if len(indices) > 5 else ''}")
    
    print(f"\n  {IMU_REGION['name']:30s} {len(IMU_REGION['data_indices']):3d} bytes")
    print(f"    Indices: {IMU_REGION['data_indices'][:5]}...{IMU_REGION['data_indices'][-1]}")
    
    # Show index coverage
    all_sensor_indices = get_all_sensor_indices()
    print(f"\nIndex coverage:")
    print(f"  Sensor data: indices {min(all_sensor_indices)} - {max(all_sensor_indices)}")
    print(f"  IMU data: indices 256 - 271")
    print(f"  Unused/reserved: ~{272 - len(all_sensor_indices) - 16} bytes")
    
    print("\n" + "=" * 80)
    print("✅ Module loaded successfully!")
    print("\nUsage Examples:")
    print("  from sensor_mapping import get_sensor_by_id, extract_all_sensor_values")
    print("  sensor = get_sensor_by_id(10)  # Get sensor 10 info")
    print("  values = extract_all_sensor_values(frame_data)  # Extract all sensor values")
    print("  stats = get_region_statistics(frame_data, 'thumb_tip')  # Get thumb tip stats")
