#!/usr/bin/env python3
"""
Quick test script for acquisition performance.

Tests:
1. Connection to serial port
2. Frame capture rate
3. Queue behavior
4. Process management
"""

import time
from acquisition_process import AcquisitionProcess


def test_acquisition(port: str, duration: int = 10):
    """
    Test acquisition process for specified duration.

    Args:
        port: Serial port path
        duration: Test duration in seconds
    """
    print("=" * 60)
    print("Acquisition Performance Test")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print(f"Target: 200+ Hz")
    print("=" * 60)

    # Create acquisition process
    acq = AcquisitionProcess(port=port, queue_maxsize=1000)

    # Start acquisition
    print("\nStarting acquisition process...")
    acq.start()
    time.sleep(0.5)  # Let it initialize

    if not acq.is_alive():
        print("ERROR: Acquisition process failed to start!")
        return

    print("✓ Acquisition process started\n")

    # Consume frames
    frame_count = 0
    start_time = time.time()
    last_display = start_time
    max_queue_depth = 0

    try:
        while time.time() - start_time < duration:
            # Get frame (non-blocking)
            frame_data = acq.get_frame(block=False)

            if frame_data is not None:
                frame_count += 1

            # Update queue stats (handle -1 on macOS)
            queue_depth = acq.get_queue_size()
            if queue_depth != -1:
                max_queue_depth = max(max_queue_depth, queue_depth)

            # Display every second
            current_time = time.time()
            if current_time - last_display >= 1.0:
                elapsed = current_time - start_time
                rate = frame_count / elapsed if elapsed > 0 else 0

                # Format queue display
                if queue_depth == -1:
                    queue_str = "N/A (max: N/A)"
                else:
                    queue_str = f"{queue_depth:4d} (max: {max_queue_depth:4d})"

                print(f"Frames: {frame_count:6d} | "
                      f"Rate: {rate:6.1f} Hz | "
                      f"Queue: {queue_str} | "
                      f"Time: {elapsed:5.1f}s")

                last_display = current_time

            # Small sleep to prevent CPU spin
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        # Stop acquisition
        print("\nStopping acquisition process...")
        acq.stop()

    # Results
    elapsed = time.time() - start_time
    avg_rate = frame_count / elapsed if elapsed > 0 else 0

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    print(f"  Total frames captured: {frame_count}")
    print(f"  Test duration: {elapsed:.2f} seconds")
    print(f"  Average capture rate: {avg_rate:.1f} Hz")
    if max_queue_depth == 0:
        print(f"  Max queue depth: N/A (not available on macOS)")
    else:
        print(f"  Max queue depth: {max_queue_depth}")
    print()

    # Evaluation
    if avg_rate >= 200:
        print("✅ SUCCESS: Achieved target rate (200+ Hz)")
    elif avg_rate >= 150:
        print("⚠️  WARNING: Below target but acceptable (150-200 Hz)")
    else:
        print(f"❌ FAILED: Rate too low ({avg_rate:.1f} Hz < 150 Hz)")

    if max_queue_depth == 0:
        print("ℹ️  Queue depth monitoring not available on macOS")
    elif max_queue_depth < 100:
        print("✅ Queue depth good (< 100 frames)")
    else:
        print(f"⚠️  Queue depth high ({max_queue_depth} frames)")

    print("=" * 60)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_acquisition_performance.py <serial_port> [duration]")
        print("Example: python test_acquisition_performance.py /dev/cu.usbmodem57640302171 10")
        sys.exit(1)

    port = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    test_acquisition(port, duration)
