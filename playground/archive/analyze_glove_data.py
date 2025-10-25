#!/usr/bin/env python3
"""
Analyze JQ Glove binary data files
Parse packets and map sensor data to glove pressure map

Based on documentation:
- Glove model: Left Hand (162 sensing points)
- Product: JQ20-XL-11
- Data format: [AA 55 03 99] + [Packet Index] + [Sensor Type] + [Data]
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Protocol definition
PACKET_DELIMITER = bytes([0xAA, 0x55, 0x03, 0x99])

# Sensor-to-data index mapping (from documentation)
# Based on the mapping table for Left Hand (162 sensing points)
SENSOR_REGIONS = {
    'little_finger': {
        'name': '小拇指 (Little Finger)',
        'sensor_ids': list(range(1, 13)),  # Sensor IDs 1-12
        'data_indices': [31, 30, 29, 15, 14, 13, 254, 255, 253, 252, 251, 250],
        'color': 'purple'
    },
    'ring_finger': {
        'name': '无名指 (Ring Finger)',
        'sensor_ids': list(range(13, 25)),  # Sensor IDs 13-24
        'data_indices': [28, 27, 26, 12, 11, 10, 252, 251, 250, 234, 235, 236],
        'color': 'blue'
    },
    'middle_finger': {
        'name': '中指 (Middle Finger)',
        'sensor_ids': list(range(25, 37)),  # Sensor IDs 25-36
        'data_indices': [25, 24, 23, 9, 8, 7, 248, 249, 247, 233, 232, 231],
        'color': 'green'
    },
    'index_finger': {
        'name': '食指 (Index Finger)',
        'sensor_ids': list(range(37, 49)),  # Sensor IDs 37-48
        'data_indices': [22, 21, 20, 6, 5, 4, 246, 244, 245, 239, 230, 229, 228],
        'color': 'orange'
    },
    'thumb': {
        'name': '大拇指 (Thumb)',
        'sensor_ids': list(range(49, 61)),  # Sensor IDs 49-60
        'data_indices': [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225],
        'color': 'red'
    },
    'little_finger_back': {
        'name': '小拇指背 (Little Finger Back)',
        'sensor_ids': [61],
        'data_indices': [222],
        'color': 'purple'
    },
    'ring_finger_back': {
        'name': '无名指背 (Ring Finger Back)',
        'sensor_ids': [62],
        'data_indices': [219],
        'color': 'blue'
    },
    'middle_finger_back': {
        'name': '中指背 (Middle Finger Back)',
        'sensor_ids': [63],
        'data_indices': [216],
        'color': 'green'
    },
    'index_finger_back': {
        'name': '食指背 (Index Finger Back)',
        'sensor_ids': [64],
        'data_indices': [213],
        'color': 'orange'
    },
    'thumb_back': {
        'name': '大拇指背 (Thumb Back)',
        'sensor_ids': [65],
        'data_indices': [210],
        'color': 'red'
    },
    'palm': {
        'name': '手掌 (Palm)',
        'sensor_ids': list(range(66, 138)),  # Sensor IDs 66-137
        'data_indices': [147, 146, 145, 143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 149, 148],
        'color': 'cyan'
    },
    'wrist': {
        'name': '左手掌腕 (Wrist)',
        'sensor_ids': list(range(1, 138)),  # Sensor IDs 1-137
        'data_indices': list(range(47, 184)),
        'color': 'gray'
    }
}

# Build complete sensor-to-data-index mapping
def build_sensor_mapping():
    """Build complete mapping from sensor ID to data index"""
    sensor_map = {}
    for region_name, region_data in SENSOR_REGIONS.items():
        sensor_ids = region_data['sensor_ids']
        data_indices = region_data['data_indices']
        
        # Map each sensor ID to its corresponding data index
        for i, sensor_id in enumerate(sensor_ids):
            if i < len(data_indices):
                sensor_map[sensor_id] = {
                    'data_index': data_indices[i],
                    'region': region_name,
                    'region_name': region_data['name'],
                    'color': region_data['color']
                }
    
    return sensor_map

SENSOR_MAP = build_sensor_mapping()

def split_packets(data, delimiter):
    """Split data stream into packets based on delimiter"""
    packets = []
    start = 0
    
    while True:
        pos = data.find(delimiter, start)
        if pos == -1:
            break
        
        if start > 0:
            packet = data[start:pos]
            if len(packet) > 0:
                packets.append(packet)
        
        start = pos + len(delimiter)
    
    if start < len(data):
        packet = data[start:]
        if len(packet) > 0:
            packets.append(packet)
    
    return packets

def parse_packet(packet):
    """
    Parse packet structure:
    [Packet Index: 1 byte] + [Sensor Type: 1 byte] + [Data: remaining bytes]
    
    Returns: (packet_index, sensor_type, data_bytes)
    """
    if len(packet) < 2:
        return None, None, None
    
    packet_index = packet[0]
    sensor_type = packet[1]
    data_bytes = packet[2:]
    
    return packet_index, sensor_type, data_bytes

def bytes_to_decimal_array(data_bytes):
    """Convert bytes to decimal values"""
    return [int(b) for b in data_bytes]

def combine_frame_packets(packet1_data, packet2_data):
    """
    Combine packet 0x01 and 0x02 data to form complete frame
    Packet 0x01: 128 bytes (1024 bits)
    Packet 0x02: 144 bytes (1152 bits)
    Total: 272 bytes = 2176 bits
    """
    # Convert to decimal arrays
    data1 = bytes_to_decimal_array(packet1_data)
    data2 = bytes_to_decimal_array(packet2_data)
    
    # Combine both packets
    combined = data1 + data2
    
    return combined

def extract_sensor_values(frame_data):
    """
    Extract sensor values from frame data using the sensor mapping
    Returns: dict of {sensor_id: value}
    """
    sensor_values = {}
    
    for sensor_id, mapping_info in SENSOR_MAP.items():
        data_index = mapping_info['data_index']
        
        # Ensure data index is within bounds
        if data_index < len(frame_data):
            value = frame_data[data_index]
            sensor_values[sensor_id] = {
                'value': value,
                'region': mapping_info['region'],
                'region_name': mapping_info['region_name'],
                'color': mapping_info['color']
            }
    
    return sensor_values

def get_region_statistics(sensor_values):
    """Calculate statistics per region"""
    region_stats = {}
    
    for sensor_id, sensor_data in sensor_values.items():
        region = sensor_data['region']
        value = sensor_data['value']
        
        if region not in region_stats:
            region_stats[region] = {
                'name': sensor_data['region_name'],
                'values': [],
                'color': sensor_data['color']
            }
        
        region_stats[region]['values'].append(value)
    
    # Calculate statistics
    for region, data in region_stats.items():
        values = data['values']
        non_zero = [v for v in values if v > 0]
        
        data['count'] = len(values)
        data['non_zero_count'] = len(non_zero)
        data['mean'] = np.mean(values) if values else 0
        data['max'] = max(values) if values else 0
        data['min'] = min(values) if values else 0
        data['non_zero_mean'] = np.mean(non_zero) if non_zero else 0
    
    return region_stats

def visualize_hand_pressure(sensor_values, output_file=None, title="Left Hand Pressure Map"):
    """
    Create a visualization of pressure data on a hand shape
    """
    fig, ax = plt.subplots(figsize=(12, 16))
    
    # Define approximate positions for each region (simplified hand model)
    # Coordinates are (x, y) with origin at bottom-left
    region_positions = {
        'thumb': [(2, y) for y in np.linspace(4, 10, 12)],
        'index_finger': [(5, y) for y in np.linspace(10, 16, 12)],
        'middle_finger': [(7, y) for y in np.linspace(10, 17, 12)],
        'ring_finger': [(9, y) for y in np.linspace(10, 16, 12)],
        'little_finger': [(11, y) for y in np.linspace(9, 14, 12)],
        'palm': [(x, y) for x in np.linspace(4, 10, 6) for y in np.linspace(3, 8, 12)],
        'thumb_back': [(2, 10.5)],
        'index_finger_back': [(5, 16.5)],
        'middle_finger_back': [(7, 17.5)],
        'ring_finger_back': [(9, 16.5)],
        'little_finger_back': [(11, 14.5)],
    }
    
    # Get max value for color scaling
    all_values = [s['value'] for s in sensor_values.values()]
    max_value = max(all_values) if all_values else 1
    
    # Plot each sensor
    for sensor_id, sensor_data in sensor_values.items():
        region = sensor_data['region']
        value = sensor_data['value']
        
        # Skip wrist for now (too many sensors)
        if region == 'wrist':
            continue
        
        # Get position for this sensor
        if region in region_positions:
            positions = region_positions[region]
            sensor_index = sensor_id - SENSOR_REGIONS[region]['sensor_ids'][0]
            
            if sensor_index < len(positions):
                x, y = positions[sensor_index]
                
                # Color intensity based on pressure value
                intensity = value / max_value if max_value > 0 else 0
                
                # Draw sensor as circle
                if value > 0:
                    circle = plt.Circle((x, y), 0.3, color=plt.cm.hot(intensity), 
                                      alpha=0.8, zorder=2)
                    ax.add_patch(circle)
                    # Add value label for non-zero values
                    ax.text(x, y, str(int(value)), ha='center', va='center', 
                           fontsize=6, fontweight='bold', zorder=3)
                else:
                    circle = plt.Circle((x, y), 0.2, color='lightgray', 
                                      alpha=0.3, zorder=1)
                    ax.add_patch(circle)
    
    # Draw simplified hand outline
    # Palm
    palm_rect = patches.Rectangle((3.5, 2), 8, 6, linewidth=2, 
                                  edgecolor='black', facecolor='none')
    ax.add_patch(palm_rect)
    
    # Fingers
    finger_width = 1.2
    # Thumb
    thumb_rect = patches.Rectangle((1.4, 4), finger_width, 6, linewidth=2,
                                   edgecolor='black', facecolor='none')
    ax.add_patch(thumb_rect)
    # Index
    index_rect = patches.Rectangle((4.4, 9), finger_width, 7, linewidth=2,
                                   edgecolor='black', facecolor='none')
    ax.add_patch(index_rect)
    # Middle
    middle_rect = patches.Rectangle((6.4, 9), finger_width, 8, linewidth=2,
                                    edgecolor='black', facecolor='none')
    ax.add_patch(middle_rect)
    # Ring
    ring_rect = patches.Rectangle((8.4, 9), finger_width, 7, linewidth=2,
                                  edgecolor='black', facecolor='none')
    ax.add_patch(ring_rect)
    # Little
    little_rect = patches.Rectangle((10.4, 9), finger_width, 5, linewidth=2,
                                    edgecolor='black', facecolor='none')
    ax.add_patch(little_rect)
    
    # Labels
    ax.text(2, 1, 'Thumb\n大拇指', ha='center', fontsize=10)
    ax.text(5, 1, 'Index\n食指', ha='center', fontsize=10)
    ax.text(7, 1, 'Middle\n中指', ha='center', fontsize=10)
    ax.text(9, 1, 'Ring\n无名指', ha='center', fontsize=10)
    ax.text(11, 1, 'Little\n小拇指', ha='center', fontsize=10)
    ax.text(7, 5, 'Palm\n手掌', ha='center', fontsize=12, fontweight='bold')
    
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 18)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.hot, 
                               norm=plt.Normalize(vmin=0, vmax=max_value))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', 
                       pad=0.05, fraction=0.046)
    cbar.set_label('Pressure Value (ADC Reading)', fontsize=12)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n✓ Visualization saved to: {output_file}")
    
    plt.show()
    
    return fig

def analyze_bin_file(filepath):
    """Analyze a binary data file"""
    print(f"Analyzing file: {filepath}")
    print("=" * 70)
    
    # Read binary file
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    
    # Split into packets
    packets = split_packets(data, PACKET_DELIMITER)
    print(f"Found {len(packets)} packets")
    
    # Parse packets
    parsed_packets = []
    for packet in packets:
        pkt_idx, sensor_type, data_bytes = parse_packet(packet)
        if pkt_idx is not None:
            parsed_packets.append({
                'packet_index': pkt_idx,
                'sensor_type': sensor_type,
                'data': data_bytes
            })
    
    print(f"Parsed {len(parsed_packets)} packets")
    
    # Group packets into frames (packet 0x01 + 0x02 = 1 frame)
    frames = []
    i = 0
    while i < len(parsed_packets) - 1:
        pkt1 = parsed_packets[i]
        pkt2 = parsed_packets[i + 1]
        
        # Look for 0x01 and 0x02 pair
        if pkt1['packet_index'] == 0x01 and pkt2['packet_index'] == 0x02:
            combined_data = combine_frame_packets(pkt1['data'], pkt2['data'])
            frames.append(combined_data)
            i += 2
        elif pkt1['packet_index'] == 0x02 and pkt2['packet_index'] == 0x01:
            combined_data = combine_frame_packets(pkt2['data'], pkt1['data'])
            frames.append(combined_data)
            i += 2
        else:
            i += 1
    
    print(f"Extracted {len(frames)} complete frames")
    
    if frames:
        print(f"\nFrame structure:")
        print(f"  Bytes per frame: {len(frames[0])}")
        print(f"  Bits per frame: {len(frames[0]) * 8}")
        
        # Analyze first frame
        print(f"\n" + "=" * 70)
        print("FIRST FRAME ANALYSIS")
        print("=" * 70)
        
        first_frame = frames[0]
        
        # Extract sensor values using mapping
        print(f"\nExtracting sensor values from frame data...")
        sensor_values = extract_sensor_values(first_frame)
        print(f"✓ Extracted {len(sensor_values)} sensor values")
        
        # Get region statistics
        region_stats = get_region_statistics(sensor_values)
        
        print(f"\n📊 Pressure by Region:")
        print("-" * 70)
        for region, stats in region_stats.items():
            if stats['non_zero_count'] > 0:
                print(f"\n  {stats['name']}:")
                print(f"    Sensors: {stats['count']} total, {stats['non_zero_count']} active")
                print(f"    Values: max={stats['max']:.0f}, mean={stats['non_zero_mean']:.1f}")
        
        # Show raw data statistics
        non_zero_values = [v for v in first_frame if v != 0]
        print(f"\n📈 Raw data statistics:")
        print(f"  Total values: {len(first_frame)}")
        print(f"  Non-zero values: {len(non_zero_values)}")
        print(f"  Zero values: {len(first_frame) - len(non_zero_values)}")
        
        if non_zero_values:
            print(f"  Min (non-zero): {min(non_zero_values)}")
            print(f"  Max: {max(non_zero_values)}")
            print(f"  Mean (non-zero): {np.mean(non_zero_values):.2f}")
        
        # Show distribution across all frames
        if len(frames) > 1:
            print(f"\n" + "=" * 70)
            print("MULTI-FRAME ANALYSIS")
            print("=" * 70)
            
            # Calculate statistics across all frames
            all_values = []
            for frame in frames[:10]:  # Analyze first 10 frames
                all_values.extend([v for v in frame if v != 0])
            
            if all_values:
                print(f"\nAggregated statistics (first 10 frames):")
                print(f"  Total non-zero values: {len(all_values)}")
                print(f"  Min: {min(all_values)}")
                print(f"  Max: {max(all_values)}")
                print(f"  Mean: {np.mean(all_values):.2f}")
                print(f"  Std: {np.std(all_values):.2f}")
    
    return frames, parsed_packets

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_glove_data.py <binary_file.bin> [--visualize]")
        print("\nExample:")
        print("  python analyze_glove_data.py glove_data_20251024_214706.bin")
        print("  python analyze_glove_data.py glove_data_20251024_214706.bin --visualize")
        sys.exit(1)
    
    filepath = sys.argv[1]
    visualize = '--visualize' in sys.argv or '-v' in sys.argv
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    frames, packets = analyze_bin_file(filepath)
    
    # Generate visualization if frames were extracted
    if frames and len(frames) > 0:
        print(f"\n" + "=" * 70)
        print("GENERATING VISUALIZATION")
        print("=" * 70)
        
        # Use first frame for visualization
        first_frame = frames[0]
        sensor_values = extract_sensor_values(first_frame)
        
        # Generate output filename
        base_name = Path(filepath).stem
        output_image = f"{base_name}_pressure_map.png"
        
        print(f"\nCreating hand pressure visualization...")
        visualize_hand_pressure(sensor_values, output_file=output_image,
                               title=f"Left Hand Pressure Map - Frame 1\n({Path(filepath).name})")
        
        # Print summary
        region_stats = get_region_statistics(sensor_values)
        active_regions = [stats['name'] for stats in region_stats.values() 
                         if stats['non_zero_count'] > 0]
        
        if active_regions:
            print(f"\n📍 Active regions detected:")
            for region_name in active_regions:
                print(f"  • {region_name}")
    
    print(f"\n✓ Analysis complete!")

if __name__ == "__main__":
    main()

