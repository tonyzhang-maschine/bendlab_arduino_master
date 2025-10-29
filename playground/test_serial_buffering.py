#!/usr/bin/env python3
"""
Test different serial reading strategies to understand buffering behavior.
"""

import serial
import time
import sys
from glove_parser import GloveParser


def test_strategy_1_immediate(port: str, duration: float = 2.0):
    """Strategy 1: Read immediately when data available (current approach)"""
    print("\n" + "=" * 60)
    print("Strategy 1: Immediate Read (current)")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=1.0)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    total_bytes = 0
    read_count = 0

    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            total_bytes += len(chunk)
            read_count += 1

            frames = parser.add_data(chunk)
            frame_count += len(frames)

        time.sleep(0.001)  # 1ms

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    return frame_count / elapsed


def test_strategy_2_batched(port: str, duration: float = 2.0):
    """Strategy 2: Wait for more data to accumulate before reading"""
    print("\n" + "=" * 60)
    print("Strategy 2: Batched Read (wait 10ms)")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=1.0)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    total_bytes = 0
    read_count = 0

    while time.time() - start_time < duration:
        # Wait for data to accumulate
        time.sleep(0.010)  # 10ms

        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            total_bytes += len(chunk)
            read_count += 1

            frames = parser.add_data(chunk)
            frame_count += len(frames)

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    return frame_count / elapsed


def test_strategy_3_fixed_size(port: str, duration: float = 2.0):
    """Strategy 3: Read fixed-size chunks"""
    print("\n" + "=" * 60)
    print("Strategy 3: Fixed-size Read (1024 bytes)")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.1)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    total_bytes = 0
    read_count = 0

    while time.time() - start_time < duration:
        # Read fixed size
        chunk = ser.read(1024)
        if chunk:
            total_bytes += len(chunk)
            read_count += 1

            frames = parser.add_data(chunk)
            frame_count += len(frames)

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    return frame_count / elapsed


def test_strategy_4_continuous(port: str, duration: float = 2.0):
    """Strategy 4: Read continuously without checking in_waiting"""
    print("\n" + "=" * 60)
    print("Strategy 4: Continuous Read (no in_waiting check)")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.01)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    total_bytes = 0
    read_count = 0

    while time.time() - start_time < duration:
        # Read up to 2048 bytes (don't check in_waiting)
        chunk = ser.read(2048)
        if chunk:
            total_bytes += len(chunk)
            read_count += 1

            frames = parser.add_data(chunk)
            frame_count += len(frames)

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    return frame_count / elapsed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_serial_buffering.py <serial_port>")
        sys.exit(1)

    port = sys.argv[1]

    print("=" * 60)
    print("Serial Buffering Strategy Comparison")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Target: 200+ Hz")
    print("=" * 60)

    try:
        rate1 = test_strategy_1_immediate(port)
        time.sleep(0.5)

        rate2 = test_strategy_2_batched(port)
        time.sleep(0.5)

        rate3 = test_strategy_3_fixed_size(port)
        time.sleep(0.5)

        rate4 = test_strategy_4_continuous(port)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Strategy 1 (immediate):     {rate1:6.1f} Hz")
        print(f"Strategy 2 (batched 10ms):  {rate2:6.1f} Hz")
        print(f"Strategy 3 (fixed 1024B):   {rate3:6.1f} Hz")
        print(f"Strategy 4 (continuous):    {rate4:6.1f} Hz")
        print("=" * 60)

        best_rate = max(rate1, rate2, rate3, rate4)
        if best_rate >= 200:
            print(f"✅ Best strategy achieved target: {best_rate:.1f} Hz")
        else:
            print(f"❌ All strategies below target (best: {best_rate:.1f} Hz)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
