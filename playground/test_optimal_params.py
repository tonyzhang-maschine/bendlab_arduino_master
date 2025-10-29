#!/usr/bin/env python3
"""
Find optimal read size and timeout parameters for 237 Hz target.
"""

import serial
import time
import sys
from glove_parser import GloveParser


def test_params(port: str, read_size: int, timeout: float, duration: float = 3.0):
    """Test with specific read size and timeout"""
    ser = serial.Serial(port, 921600, timeout=timeout)
    ser.reset_input_buffer()
    time.sleep(0.1)

    parser = GloveParser()
    frame_count = 0
    start_time = time.time()
    read_count = 0
    total_bytes = 0

    while time.time() - start_time < duration:
        data = ser.read(read_size)
        if data:
            total_bytes += len(data)
            read_count += 1
            frame_count += len(parser.add_data(data))

    elapsed = time.time() - start_time
    ser.close()

    rate = frame_count / elapsed
    avg_bytes_per_read = total_bytes / read_count if read_count > 0 else 0

    return rate, read_count, avg_bytes_per_read


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_optimal_params.py <serial_port>")
        sys.exit(1)

    port = sys.argv[1]

    print("=" * 70)
    print("Parameter Optimization Grid Search")
    print("=" * 70)
    print("Target: 237 Hz")
    print("=" * 70)
    print()

    # Test matrix
    read_sizes = [1024, 2048, 4096, 8192]
    timeouts = [0.005, 0.01, 0.02, 0.03, 0.05]

    results = []

    for read_size in read_sizes:
        for timeout in timeouts:
            print(f"Testing: read_size={read_size:4d}, timeout={timeout*1000:4.1f}ms ... ", end='', flush=True)

            try:
                rate, reads, avg_bytes = test_params(port, read_size, timeout, duration=2.0)
                results.append((rate, read_size, timeout, reads, avg_bytes))

                status = "✅" if rate >= 200 else "⚠️" if rate >= 150 else "❌"
                print(f"{rate:6.1f} Hz {status}")

                time.sleep(0.3)  # Brief pause between tests

            except Exception as e:
                print(f"ERROR: {e}")

    # Sort by rate
    results.sort(reverse=True)

    print("\n" + "=" * 70)
    print("Top 10 Configurations:")
    print("=" * 70)
    print(f"{'Rank':<6} {'Rate':>8} {'Read Size':>10} {'Timeout':>10} {'Reads/sec':>10} {'Avg B/read':>12}")
    print("-" * 70)

    for i, (rate, read_size, timeout, reads, avg_bytes) in enumerate(results[:10], 1):
        reads_per_sec = reads / 2.0  # We tested for 2 seconds
        status = "✅" if rate >= 200 else "⚠️" if rate >= 150 else ""
        print(f"{i:<6} {rate:8.1f} {read_size:10d} {timeout*1000:9.1f}ms {reads_per_sec:10.1f} {avg_bytes:12.1f} {status}")

    print("=" * 70)

    if results and results[0][0] >= 200:
        best_rate, best_size, best_timeout, _, _ = results[0]
        print(f"\n✅ SUCCESS! Best configuration achieves {best_rate:.1f} Hz")
        print(f"   Recommended: READ_SIZE={best_size}, timeout={best_timeout}")
    else:
        print(f"\n⚠️  Best achieved: {results[0][0]:.1f} Hz (target: 237 Hz)")
        print(f"   Gap: {237 - results[0][0]:.1f} Hz")
