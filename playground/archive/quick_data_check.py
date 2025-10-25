#!/usr/bin/env python3
"""Quick check to see what's in the raw data"""

import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "glove_data_20251024_214706.bin"

with open(filename, 'rb') as f:
    data = f.read()

# Find delimiter positions
DELIM = bytes([0xAA, 0x55, 0x03, 0x99])
positions = []
pos = 0
while True:
    pos = data.find(DELIM, pos)
    if pos == -1:
        break
    positions.append(pos)
    pos += 1

print(f"Found {len(positions)} delimiters")

# Extract first complete packet
if len(positions) >= 2:
    start = positions[0] + 4  # Skip delimiter
    end = positions[1]
    packet = data[start:end]
    
    print(f"\nFirst packet: {len(packet)} bytes")
    print(f"Packet index: 0x{packet[0]:02X}")
    print(f"Sensor type: 0x{packet[1]:02X}")
    
    payload = packet[2:]
    print(f"\nPayload: {len(payload)} bytes")
    
    # Show non-zero values
    non_zero = [(i, b) for i, b in enumerate(payload) if b != 0]
    print(f"Non-zero values: {len(non_zero)}")
    for i, (idx, val) in enumerate(non_zero[:20]):
        print(f"  Index {idx:3d}: {val:3d} (0x{val:02X})")

