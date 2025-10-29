#!/usr/bin/env python3
"""
Detailed timing analysis to identify bottleneck in read-parse loop.
"""

import serial
import time
import sys
from glove_parser import GloveParser


def test_with_timing(port: str, duration: float = 5.0):
    """Test with detailed timing measurements"""
    print("=" * 60)
    print("Detailed Timing Analysis")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.01)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()

    # Timing measurements
    total_read_time = 0
    total_parse_time = 0
    total_queue_time = 0
    read_count = 0
    total_bytes = 0

    print(f"Testing for {duration} seconds with 1024-byte reads...\n")

    while time.time() - start_time < duration:
        # Measure read time
        t0 = time.time()
        data = ser.read(1024)
        t1 = time.time()
        read_time = t1 - t0

        if data:
            total_read_time += read_time
            total_bytes += len(data)
            read_count += 1

            # Measure parse time
            t2 = time.time()
            frames = parser.add_data(data)
            t3 = time.time()
            parse_time = t3 - t2
            total_parse_time += parse_time

            # Simulate queue put (measure time)
            t4 = time.time()
            for frame in frames:
                # Simulate minimal processing
                _ = len(frame)
            t5 = time.time()
            queue_time = t5 - t4
            total_queue_time += queue_time

            frame_count += len(frames)

    elapsed = time.time() - start_time
    ser.close()

    # Results
    print("=" * 60)
    print("Results:")
    print("=" * 60)
    print(f"Duration: {elapsed:.2f} seconds")
    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    print(f"\nTiming breakdown:")
    print(f"  Total read time:  {total_read_time*1000:.1f} ms ({100*total_read_time/elapsed:.1f}%)")
    print(f"  Total parse time: {total_parse_time*1000:.1f} ms ({100*total_parse_time/elapsed:.1f}%)")
    print(f"  Total queue time: {total_queue_time*1000:.1f} ms ({100*total_queue_time/elapsed:.1f}%)")
    print(f"  Other/overhead:   {(elapsed - total_read_time - total_parse_time - total_queue_time)*1000:.1f} ms ({100*(elapsed - total_read_time - total_parse_time - total_queue_time)/elapsed:.1f}%)")

    print(f"\nPer-operation averages:")
    print(f"  Avg read time:  {total_read_time/read_count*1000 if read_count > 0 else 0:.3f} ms/read")
    print(f"  Avg parse time: {total_parse_time/read_count*1000 if read_count > 0 else 0:.3f} ms/read")

    # Calculate theoretical max based on read time
    theoretical_max = 1.0 / (total_read_time/read_count) * (frame_count/read_count) if read_count > 0 else 0
    print(f"\nTheoretical max rate (based on read time): {theoretical_max:.1f} Hz")

    return frame_count / elapsed


def test_with_larger_reads(port: str, duration: float = 5.0):
    """Test with larger read size to reduce overhead"""
    print("\n" + "=" * 60)
    print("Test with Larger Reads (4096 bytes)")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.02)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    read_count = 0
    total_bytes = 0

    while time.time() - start_time < duration:
        data = ser.read(4096)
        if data:
            total_bytes += len(data)
            read_count += 1
            frames = parser.add_data(data)
            frame_count += len(frames)

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    return frame_count / elapsed


def test_with_smaller_timeout(port: str, duration: float = 5.0):
    """Test with smaller timeout for more responsive reads"""
    print("\n" + "=" * 60)
    print("Test with Smaller Timeout (5ms)")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.005)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    read_count = 0
    total_bytes = 0

    while time.time() - start_time < duration:
        data = ser.read(2048)
        if data:
            total_bytes += len(data)
            read_count += 1
            frames = parser.add_data(data)
            frame_count += len(frames)

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")
    print(f"Bytes: {total_bytes} ({total_bytes/elapsed:.0f} B/s)")
    print(f"Reads: {read_count} (avg {total_bytes/read_count if read_count > 0 else 0:.1f} B/read)")

    return frame_count / elapsed


def test_minimal_overhead(port: str, duration: float = 5.0):
    """Test with absolute minimal overhead"""
    print("\n" + "=" * 60)
    print("Test with Minimal Overhead")
    print("=" * 60)

    ser = serial.Serial(port, 921600, timeout=0.005)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()

    # Tight loop, minimal overhead
    while time.time() - start_time < duration:
        data = ser.read(2048)
        if data:
            frame_count += len(parser.add_data(data))

    elapsed = time.time() - start_time
    ser.close()

    print(f"Frames: {frame_count} ({frame_count/elapsed:.1f} Hz)")

    return frame_count / elapsed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_timing_analysis.py <serial_port>")
        sys.exit(1)

    port = sys.argv[1]

    rate1 = test_with_timing(port, 3.0)
    time.sleep(0.5)

    rate2 = test_with_larger_reads(port, 3.0)
    time.sleep(0.5)

    rate3 = test_with_smaller_timeout(port, 3.0)
    time.sleep(0.5)

    rate4 = test_minimal_overhead(port, 3.0)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Current approach (1024B, 10ms):    {rate1:6.1f} Hz")
    print(f"Larger reads (4096B, 20ms):        {rate2:6.1f} Hz")
    print(f"Smaller timeout (2048B, 5ms):      {rate3:6.1f} Hz")
    print(f"Minimal overhead (2048B, 5ms):     {rate4:6.1f} Hz")
    print(f"\nTarget: 237 Hz")
    print("=" * 60)

    best = max(rate1, rate2, rate3, rate4)
    if best >= 200:
        print(f"✅ Achieved target! Best rate: {best:.1f} Hz")
    else:
        print(f"❌ Below target. Best rate: {best:.1f} Hz (gap: {237-best:.1f} Hz)")
