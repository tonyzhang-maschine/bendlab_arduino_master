#!/usr/bin/env python3
"""
Sensor-to-index mapping for JQ Glove (Left Hand)
Based on documentation diagram showing actual byte positions in 272-byte frame

The numbers in the documentation diagram represent DIRECT byte indices 
in the combined frame (packet 0x01 + packet 0x02 = 272 bytes)
"""

import numpy as np

# Sensor regions with their corresponding data indices in the frame
# These indices are the byte positions (0-271) where sensor data is located

SENSOR_REGIONS = {
    'little_finger': {
        'name': '小拇指 (Little Finger)',
        'color': 'purple',
        'data_indices': [31, 30, 29, 15, 14, 13, 255, 254, 253, 239, 238, 237]
    },
    'ring_finger': {
        'name': '无名指 (Ring Finger)', 
        'color': 'blue',
        'data_indices': [28, 27, 26, 12, 11, 10, 252, 251, 250, 236, 235, 234]
    },
    'middle_finger': {
        'name': '中指 (Middle Finger)',
        'color': 'green', 
        'data_indices': [25, 24, 23, 9, 8, 7, 249, 248, 247, 233, 232, 231]
    },
    'index_finger': {
        'name': '食指 (Index Finger)',
        'color': 'orange',
        'data_indices': [22, 21, 20, 6, 5, 4, 246, 245, 244, 230, 229, 228]
    },
    'thumb': {
        'name': '大拇指 (Thumb)',
        'color': 'red',
        'data_indices': [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225]
    },
    'little_finger_back': {
        'name': '小拇指背 (Little Finger Back)',
        'color': 'purple',
        'data_indices': [238]  # Highlighted in blue in doc
    },
    'ring_finger_back': {
        'name': '无名指背 (Ring Finger Back)', 
        'color': 'blue',
        'data_indices': [219]
    },
    'middle_finger_back': {
        'name': '中指背 (Middle Finger Back)',
        'color': 'green',
        'data_indices': [216]
    },
    'index_finger_back': {
        'name': '食指背 (Index Finger Back)',
        'color': 'orange',
        'data_indices': [213]
    },
    'thumb_back': {
        'name': '大拇指背 (Thumb Back)',
        'color': 'red',
        'data_indices': [210]
    },
    'palm': {
        'name': '手掌 (Palm)',
        'color': 'cyan',
        'data_indices': [
            # Bottom rows (near wrist)
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
    """Get all sensor data indices as a flat list"""
    all_indices = []
    for region in SENSOR_REGIONS.values():
        all_indices.extend(region['data_indices'])
    return sorted(set(all_indices))

def get_sensor_count():
    """Get total number of unique sensors"""
    return len(get_all_sensor_indices())

def extract_sensor_values(frame_data):
    """
    Extract sensor values from a 272-byte frame
    OPTIMIZED: Uses numpy operations instead of Python loops
    
    Args:
        frame_data: List or bytes of length 272 (combined packet 0x01 + 0x02)
    
    Returns:
        dict: {region_name: {'indices': [...], 'values': [...], 'color': '...'}}
    """
    if len(frame_data) < 272:
        raise ValueError(f"Frame data must be 272 bytes, got {len(frame_data)}")
    
    # Convert to numpy array if needed
    if not isinstance(frame_data, np.ndarray):
        frame_data = np.array(frame_data, dtype=np.uint8)
    
    sensor_values = {}
    
    for region_name, region_info in SENSOR_REGIONS.items():
        indices = region_info['data_indices']
        # OPTIMIZED: Use numpy fancy indexing instead of list comprehension
        indices_arr = np.array(indices, dtype=np.int32)
        values = frame_data[indices_arr]
        
        # OPTIMIZED: Use numpy operations for statistics
        sensor_values[region_name] = {
            'name': region_info['name'],
            'indices': indices,
            'values': values,
            'color': region_info['color'],
            'max': int(values.max()),
            'mean': float(values.mean()),
            'active_count': int(np.count_nonzero(values))
        }
    
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
    Find which region a data index belongs to
    
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

# Summary information
TOTAL_SENSORS = get_sensor_count()
FRAME_SIZE = 272  # bytes (packet 0x01: 128 + packet 0x02: 144)

if __name__ == "__main__":
    print("JQ Glove Sensor Mapping")
    print("=" * 60)
    print(f"\nTotal unique sensor indices: {TOTAL_SENSORS}")
    print(f"Frame size: {FRAME_SIZE} bytes")
    
    print(f"\nSensor regions:")
    for region_name, region_info in SENSOR_REGIONS.items():
        indices = region_info['data_indices']
        print(f"  {region_info['name']:30s} {len(indices):3d} sensors")
        print(f"    Indices: {indices[:5]}{'...' if len(indices) > 5 else ''}")
    
    print(f"\n  {IMU_REGION['name']:30s} {len(IMU_REGION['data_indices']):3d} bytes")
    print(f"    Indices: {IMU_REGION['data_indices'][:5]}...{IMU_REGION['data_indices'][-1]}")
    
    # Show index coverage
    all_sensor_indices = get_all_sensor_indices()
    print(f"\nIndex coverage:")
    print(f"  Sensor data: indices {min(all_sensor_indices)} - {max(all_sensor_indices)}")
    print(f"  IMU data: indices 256 - 271")
    print(f"  Unused/reserved: ~{272 - len(all_sensor_indices) - 16} bytes")
