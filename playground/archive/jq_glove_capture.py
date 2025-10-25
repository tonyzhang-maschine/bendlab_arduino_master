#!/usr/bin/env python3
"""
Simple COM port reader for JQ Glove device
Captures data and analyzes packet structure

Based on documentation:
- Baudrate: 921600 bps
- Packet delimiter: 0xAA 0x55 0x03 0x99
- Data rate: ~100Hz
"""

import serial
import time
import sys
from collections import Counter

# Configuration
PORT = '/dev/cu.usbmodem57640302171'
BAUDRATE = 921600
TIMEOUT = 1.0
CAPTURE_DURATION = 1.0  # seconds

# Protocol definition (from documentation)
PACKET_DELIMITER = bytes([0xAA, 0x55, 0x03, 0x99])

# Sensor type mapping
SENSOR_TYPES = {
    0x01: "LH (Left Hand)",
    0x02: "RH (Right Hand)",
    0x03: "LF (Left Foot)",
    0x04: "RF (Right Foot)",
    0x05: "FB (Front Body)",
    0x06: "WB (Whole Body)"
}

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

def split_packets(data, delimiter):
    """Split data stream into packets based on delimiter"""
    packets = []
    start = 0
    
    while True:
        # Find next delimiter
        pos = data.find(delimiter, start)
        if pos == -1:
            break
        
        # If this is not the first packet, save the previous one
        if start > 0:
            packet = data[start:pos]
            if len(packet) > 0:
                packets.append(packet)
        
        # Move past the delimiter
        start = pos + len(delimiter)
    
    # Add the last packet if there's data remaining
    if start < len(data):
        packet = data[start:]
        if len(packet) > 0:
            packets.append(packet)
    
    return packets

def analyze_data_patterns(data):
    """Analyze captured data to find patterns and delimiters"""
    print("\n" + "=" * 60)
    print("DATA ANALYSIS")
    print("=" * 60)
    
    # Basic stats
    print(f"\n📊 Total bytes captured: {len(data)}")
    print(f"   Expected packets (~100Hz): ~{int(CAPTURE_DURATION * 100)}")
    
    # Check for known delimiter
    delimiter_count = data.count(PACKET_DELIMITER)
    print(f"\n🔍 Delimiter [AA 55 03 99] found: {delimiter_count} times")
    
    if delimiter_count > 0:
        # Split into packets
        packets = split_packets(data, PACKET_DELIMITER)
        print(f"✓ Extracted {len(packets)} packets")
        
        if packets:
            # Parse and analyze packets
            parsed_packets = []
            for packet in packets:
                pkt_idx, sensor_type, data_bytes = parse_packet(packet)
                if pkt_idx is not None:
                    parsed_packets.append({
                        'raw': packet,
                        'packet_index': pkt_idx,
                        'sensor_type': sensor_type,
                        'data': data_bytes
                    })
            
            print(f"✓ Parsed {len(parsed_packets)} packets")
            
            # Analyze packet structure
            packet_indices = Counter([p['packet_index'] for p in parsed_packets])
            sensor_types = Counter([p['sensor_type'] for p in parsed_packets])
            data_sizes = Counter([len(p['data']) for p in parsed_packets])
            
            print(f"\n📋 Packet Index Distribution:")
            for idx, count in sorted(packet_indices.items()):
                print(f"   0x{idx:02X} ({idx:3d}): {count:3d} packets")
            
            print(f"\n🔧 Sensor Type Distribution:")
            for stype, count in sorted(sensor_types.items()):
                sensor_name = SENSOR_TYPES.get(stype, "Unknown")
                print(f"   0x{stype:02X} - {sensor_name}: {count:3d} packets")
            
            print(f"\n📦 Data Payload Size Distribution:")
            for size, count in sorted(data_sizes.items()):
                bits = size * 8
                print(f"   {size:3d} bytes ({bits:4d} bits): {count:3d} packets")
            
            # Show first few packets with detailed parsing
            print(f"\n📄 First 10 packets (parsed):")
            for i, pkt in enumerate(parsed_packets[:10]):
                pkt_idx = pkt['packet_index']
                sensor_type = pkt['sensor_type']
                sensor_name = SENSOR_TYPES.get(sensor_type, "Unknown")
                data_len = len(pkt['data'])
                
                # Show first 20 bytes of data
                data_hex = ' '.join(f'{b:02X}' for b in pkt['data'][:20])
                if len(pkt['data']) > 20:
                    data_hex += "..."
                
                print(f"\n   Packet {i+1}:")
                print(f"      Packet Index: 0x{pkt_idx:02X}")
                print(f"      Sensor Type:  0x{sensor_type:02X} ({sensor_name})")
                print(f"      Data Length:  {data_len} bytes ({data_len*8} bits)")
                print(f"      Data (first 20 bytes): {data_hex}")
        
    else:
        print("⚠️  Delimiter not found! Showing byte frequency analysis...")
        
        # Byte frequency analysis (fallback)
        byte_freq = Counter(data)
        print(f"\n🔢 Unique byte values: {len(byte_freq)}")
        print("\n   Most common bytes:")
        for byte_val, count in byte_freq.most_common(10):
            print(f"      0x{byte_val:02X} ({byte_val:3d}): {count:4d} times")
    
    # Show first 200 bytes in hex format for reference
    print(f"\n📄 Raw data - First 200 bytes (hex):")
    print_hex_dump(data[:200])
    
    return parsed_packets if delimiter_count > 0 and packets else []

def print_hex_dump(data, bytes_per_line=16):
    """Print data in hex dump format"""
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i+bytes_per_line]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"   {i:04d}: {hex_str:<48}  {ascii_str}")

def capture_and_analyze():
    """Capture data for a duration and analyze it"""
    print(f"Attempting to connect to {PORT}...")
    print(f"Baudrate: {BAUDRATE}")
    print(f"Capture duration: {CAPTURE_DURATION} seconds")
    print("-" * 60)
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=TIMEOUT,
            bytesize=8,
            parity='N',
            stopbits=1
        )
        
        print(f"✓ Connected to {PORT}")
        print(f"\n⏱️  Capturing data for {CAPTURE_DURATION} second(s)...")
        
        # Flush any existing data
        ser.reset_input_buffer()
        time.sleep(0.1)
        
        # Capture data
        all_data = bytearray()
        start_time = time.time()
        
        while time.time() - start_time < CAPTURE_DURATION:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                all_data.extend(chunk)
            time.sleep(0.001)
        
        elapsed = time.time() - start_time
        print(f"✓ Capture complete! ({elapsed:.2f}s)")
        
        # Analyze the captured data
        if all_data:
            analyze_data_patterns(all_data)
            
            # Save to file for further analysis
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"glove_data_{timestamp}.bin"
            with open(filename, 'wb') as f:
                f.write(all_data)
            print(f"\n💾 Data saved to: {filename}")
        else:
            print("\n⚠️  No data received!")
        
    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n✓ Port closed")

if __name__ == "__main__":
    capture_and_analyze()

