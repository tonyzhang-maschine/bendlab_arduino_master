#!/usr/bin/env python3
"""
Direct test of GloveParser with original serial reading approach.
This will help identify if the issue is in the parser or the multiprocessing.
"""

import serial
import time
import sys
from glove_parser import GloveParser


def test_parser_direct(port: str, duration: float = 5.0):
    """
    Test parser with direct serial read (no multiprocessing).
    Uses exact same approach as jq_glove_capture.py
    """
    print("=" * 60)
    print("Direct Parser Test (No Multiprocessing)")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print("=" * 60)

    try:
        # Open serial connection (same as jq_glove_capture.py)
        ser = serial.Serial(
            port=port,
            baudrate=921600,
            timeout=1.0,
            bytesize=8,
            parity='N',
            stopbits=1
        )

        print(f"✓ Connected to {port}")
        print(f"\n⏱️  Capturing data for {duration} second(s)...\n")

        # Flush any existing data
        ser.reset_input_buffer()
        time.sleep(0.1)

        # Create parser
        parser = GloveParser()

        # Capture data
        frame_count = 0
        start_time = time.time()
        last_display = start_time
        total_bytes = 0
        total_chunks = 0

        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                # Read all available data (same as jq_glove_capture.py)
                chunk = ser.read(ser.in_waiting)
                total_bytes += len(chunk)
                total_chunks += 1

                # Parse frames
                frames = parser.add_data(chunk)
                frame_count += len(frames)

                # Debug: Show parser state
                if frames:
                    print(f"[Chunk {total_chunks}] Read {len(chunk)} bytes → Got {len(frames)} frames")

            # Display every second
            current_time = time.time()
            if current_time - last_display >= 1.0:
                elapsed = current_time - start_time
                rate = frame_count / elapsed if elapsed > 0 else 0
                bytes_per_sec = total_bytes / elapsed if elapsed > 0 else 0

                parser_stats = parser.get_statistics()

                print(f"\n[{elapsed:.1f}s] Frames: {frame_count} | "
                      f"Rate: {rate:.1f} Hz | "
                      f"Data: {bytes_per_sec:.0f} B/s | "
                      f"Buffer: {parser_stats['buffer_size']} bytes | "
                      f"Pending: {parser_stats['pending_packet']}")

                last_display = current_time

            time.sleep(0.001)  # Same as jq_glove_capture.py

        elapsed = time.time() - start_time
        avg_rate = frame_count / elapsed if elapsed > 0 else 0
        avg_bytes = total_bytes / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 60)
        print("Results:")
        print("=" * 60)
        print(f"Frames captured: {frame_count}")
        print(f"Duration: {elapsed:.2f} seconds")
        print(f"Average rate: {avg_rate:.1f} Hz")
        print(f"Total bytes: {total_bytes} ({avg_bytes:.0f} B/s)")
        print(f"Total chunks read: {total_chunks}")
        print(f"Avg bytes per chunk: {total_bytes / total_chunks if total_chunks > 0 else 0:.1f}")

        # Parser stats
        parser_stats = parser.get_statistics()
        print(f"\nParser state:")
        print(f"  Buffer size: {parser_stats['buffer_size']} bytes")
        print(f"  Pending packet: {parser_stats['pending_packet']}")
        print(f"  Total frames parsed: {parser_stats['frame_count']}")

        # Evaluation
        print("\n" + "=" * 60)
        if avg_rate >= 200:
            print("✅ SUCCESS: Achieved target rate (200+ Hz)")
        elif avg_rate >= 150:
            print("⚠️  WARNING: Below target (150-200 Hz)")
        else:
            print(f"❌ FAILED: Rate too low ({avg_rate:.1f} Hz)")
        print("=" * 60)

        ser.close()

    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_parser_direct.py <serial_port> [duration]")
        print("Example: python test_parser_direct.py /dev/cu.usbmodem57640302171 5")
        sys.exit(1)

    port = sys.argv[1]
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    test_parser_direct(port, duration)
