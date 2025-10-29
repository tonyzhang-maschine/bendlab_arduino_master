#!/usr/bin/env python3
"""
Analyze packet ordering to understand if we're losing frames due to out-of-order packets.
"""

import serial
import time
import sys


DELIMITER = bytes([0xAA, 0x55, 0x03, 0x99])


def parse_packet_header(data):
    """Parse just the header to get packet index"""
    if len(data) < 6:
        return None
    if data[0:4] != DELIMITER:
        return None
    return data[4]  # packet_index


def analyze_packet_sequence(port: str, duration: float = 5.0):
    """Capture and analyze packet ordering"""
    print("=" * 60)
    print("Packet Order Analysis")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.01)
    ser.reset_input_buffer()
    time.sleep(0.1)

    buffer = bytearray()
    packet_sequence = []
    start_time = time.time()

    print(f"Capturing for {duration} seconds...\n")

    while time.time() - start_time < duration:
        data = ser.read(1024)
        if data:
            buffer.extend(data)

    ser.close()

    # Parse all packets from buffer
    print(f"Captured {len(buffer)} bytes total")
    print("Parsing packets...\n")

    pos = 0
    while pos < len(buffer):
        # Find delimiter
        try:
            delim_pos = buffer.index(DELIMITER, pos)
        except ValueError:
            break

        # Try to parse packet header
        if delim_pos + 6 <= len(buffer):
            packet_idx = buffer[delim_pos + 4]
            packet_sequence.append(packet_idx)

            # Skip past this packet (estimate size)
            if packet_idx == 0x01:
                pos = delim_pos + 134
            elif packet_idx == 0x02:
                pos = delim_pos + 150
            else:
                pos = delim_pos + 4  # Just skip delimiter
        else:
            break

    # Analyze sequence
    print(f"Found {len(packet_sequence)} packets")
    print("\nPacket distribution:")
    pkt_01_count = packet_sequence.count(0x01)
    pkt_02_count = packet_sequence.count(0x02)
    print(f"  Packet 0x01: {pkt_01_count}")
    print(f"  Packet 0x02: {pkt_02_count}")

    # Check for expected alternating pattern
    print("\nExpected pattern: 0x01, 0x02, 0x01, 0x02, ...")
    print("Actual sequence (first 20 packets):")
    for i, pkt_idx in enumerate(packet_sequence[:20]):
        expected = 0x01 if i % 2 == 0 else 0x02
        match = "✓" if pkt_idx == expected else "✗"
        print(f"  {i:3d}: 0x{pkt_idx:02X} (expected 0x{expected:02X}) {match}")

    # Count mismatches
    mismatches = 0
    for i, pkt_idx in enumerate(packet_sequence):
        expected = 0x01 if i % 2 == 0 else 0x02
        if pkt_idx != expected:
            mismatches += 1

    print(f"\nTotal mismatches: {mismatches} / {len(packet_sequence)} ({100*mismatches/len(packet_sequence):.1f}%)")

    # Theoretical max frames
    theoretical_frames = min(pkt_01_count, pkt_02_count)
    print(f"\nTheoretical max frames: {theoretical_frames}")
    print(f"  (limited by min(packet_01={pkt_01_count}, packet_02={pkt_02_count}))")

    # Look for problematic patterns
    print("\nProblematic patterns:")
    consecutive_01 = 0
    consecutive_02 = 0
    orphan_02 = 0  # 0x02 without preceding 0x01

    prev = None
    for pkt_idx in packet_sequence:
        if pkt_idx == 0x01:
            if prev == 0x01:
                consecutive_01 += 1
        elif pkt_idx == 0x02:
            if prev == 0x02:
                consecutive_02 += 1
            if prev is None:
                orphan_02 += 1
        prev = pkt_idx

    print(f"  Consecutive 0x01 packets: {consecutive_01}")
    print(f"  Consecutive 0x02 packets: {consecutive_02}")
    print(f"  Orphan 0x02 (no preceding 0x01): {orphan_02}")

    if mismatches == 0:
        print("\n✅ Perfect alternating sequence!")
    elif mismatches < len(packet_sequence) * 0.05:
        print("\n✅ Nearly perfect sequence (< 5% errors)")
    else:
        print(f"\n❌ Significant ordering issues ({100*mismatches/len(packet_sequence):.1f}% errors)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_packet_order.py <serial_port>")
        sys.exit(1)

    port = sys.argv[1]
    analyze_packet_sequence(port)
