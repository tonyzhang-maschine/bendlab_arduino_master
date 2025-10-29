#!/usr/bin/env python3
"""
Test acquisition_process WITHOUT GUI - verifies core functionality.
This can be run headless (no display required).
"""

import sys
import time
from acquisition_process import AcquisitionProcess


def test_acquisition(port: str, duration: float = 10.0):
    """Test acquisition process without GUI"""
    print("=" * 60)
    print("Acquisition Process Test (No GUI)")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print("=" * 60)
    print()

    # Start acquisition
    acq = AcquisitionProcess(port)
    acq.start()

    if not acq.is_alive():
        print("❌ FAILED: Acquisition process did not start")
        return False

    print("✅ Acquisition process started")
    print()

    # Collect data
    frame_count = 0
    start_time = time.time()
    last_display = start_time

    try:
        while time.time() - start_time < duration:
            # Get frame
            frame_data = acq.get_frame(block=False)

            if frame_data is not None:
                frame_count += 1

            # Display stats every second
            current_time = time.time()
            if current_time - last_display >= 1.0:
                elapsed = current_time - start_time
                rate = frame_count / elapsed if elapsed > 0 else 0

                # Get acquisition stats
                stats = acq.get_stats(block=False)
                if stats:
                    acq_rate = stats.get('capture_rate_hz', 0)
                    queue_depth = stats.get('queue_depth', -1)
                    print(f"[{elapsed:5.1f}s] Frames: {frame_count:5d} | "
                          f"Consumer Rate: {rate:6.1f} Hz | "
                          f"Acquisition: {acq_rate:6.1f} Hz | "
                          f"Queue: {queue_depth if queue_depth >= 0 else 'N/A'}")
                else:
                    print(f"[{elapsed:5.1f}s] Frames: {frame_count:5d} | "
                          f"Rate: {rate:6.1f} Hz")

                last_display = current_time

            time.sleep(0.001)  # Small sleep to prevent CPU spin

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        # Stop acquisition
        print("\nStopping acquisition...")
        acq.stop()

    # Final stats
    elapsed = time.time() - start_time
    avg_rate = frame_count / elapsed if elapsed > 0 else 0

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    print(f"Frames received: {frame_count}")
    print(f"Duration: {elapsed:.2f} seconds")
    print(f"Average rate: {avg_rate:.1f} Hz")
    print()

    # Evaluation
    if avg_rate >= 200:
        print("✅ SUCCESS: Achieved 200+ Hz")
        return True
    elif avg_rate >= 150:
        print("⚠️  WARNING: Below target but acceptable (150-200 Hz)")
        return True
    else:
        print(f"❌ FAILED: Rate too low ({avg_rate:.1f} Hz)")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_acquisition_only.py <serial_port> [duration]")
        print("Example: python test_acquisition_only.py /dev/cu.usbmodem57640302171 10")
        sys.exit(1)

    port = sys.argv[1]
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    success = test_acquisition(port, duration)
    sys.exit(0 if success else 1)
