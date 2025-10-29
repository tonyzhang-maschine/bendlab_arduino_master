#!/usr/bin/env python3
"""
Data Acquisition Process - High-priority process for serial data capture

Runs independently from GUI at full hardware rate (200+ Hz).
Communicates via multiprocessing.Queue for process-safe data sharing.

Architecture:
    Serial Port → Parser → Queue → [GUI, Logger, LSL]

Performance Target:
    - 200+ Hz sustained capture
    - <50ms latency
    - Zero frame drops
    - CPU: <20%
"""

import serial
import time
import sys
from multiprocessing import Process, Queue, Event
from typing import Optional, Dict
import numpy as np
from glove_parser import GloveParser


class AcquisitionProcess:
    """
    High-priority data acquisition process.

    Reads from USB serial at full hardware rate and pushes frames to queue.
    Designed to run independently of GUI/display processes.
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 921600,
        queue_maxsize: int = 1000,  # 5 seconds at 200 Hz
        timeout: float = 1.0
    ):
        """
        Initialize acquisition process.

        Args:
            port: Serial port path (e.g., '/dev/cu.usbmodem...')
            baudrate: Serial baud rate (default: 921600)
            queue_maxsize: Maximum queue size (default: 1000 frames)
            timeout: Serial read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        # Inter-process communication
        self.frame_queue = Queue(maxsize=queue_maxsize)
        self.stats_queue = Queue(maxsize=10)
        self.stop_event = Event()

        # Process handle
        self.process: Optional[Process] = None

    def start(self):
        """Start the acquisition process."""
        if self.process is not None and self.process.is_alive():
            print("Warning: Acquisition process already running")
            return

        self.stop_event.clear()
        self.process = Process(
            target=self._acquisition_loop,
            args=(
                self.port,
                self.baudrate,
                self.timeout,
                self.frame_queue,
                self.stats_queue,
                self.stop_event
            ),
            name="AcquisitionProcess"
        )
        self.process.start()
        print(f"Started acquisition process (PID: {self.process.pid})")

    def stop(self, timeout: float = 5.0):
        """
        Stop the acquisition process gracefully.

        Args:
            timeout: Maximum time to wait for process to stop (seconds)
        """
        if self.process is None:
            return

        print("Stopping acquisition process...")
        self.stop_event.set()
        self.process.join(timeout=timeout)

        if self.process.is_alive():
            print("Warning: Process did not stop gracefully, terminating...")
            self.process.terminate()
            self.process.join(timeout=1.0)

        self.process = None
        print("Acquisition process stopped")

    def get_frame(self, block: bool = True, timeout: Optional[float] = None) -> Optional[Dict]:
        """
        Get next frame from queue.

        Args:
            block: Whether to block waiting for frame
            timeout: Maximum time to wait (None = infinite)

        Returns:
            dict with keys: 'frame' (numpy array), 'timestamp' (float)
            or None if queue is empty (when block=False)
        """
        try:
            return self.frame_queue.get(block=block, timeout=timeout)
        except:
            return None

    def get_stats(self, block: bool = False) -> Optional[Dict]:
        """
        Get latest statistics from acquisition process.

        Args:
            block: Whether to block waiting for stats

        Returns:
            dict with statistics or None if not available
        """
        try:
            return self.stats_queue.get(block=block, timeout=0.1)
        except:
            return None

    def is_alive(self) -> bool:
        """Check if acquisition process is running."""
        return self.process is not None and self.process.is_alive()

    def get_queue_size(self) -> int:
        """
        Get current queue depth.

        Note: Returns -1 on macOS where qsize() is not implemented.
        """
        try:
            return self.frame_queue.qsize()
        except NotImplementedError:
            # macOS doesn't implement qsize()
            return -1

    @staticmethod
    def _acquisition_loop(
        port: str,
        baudrate: int,
        timeout: float,
        frame_queue: Queue,
        stats_queue: Queue,
        stop_event: Event
    ):
        """
        Main acquisition loop - runs in separate process.

        This is a static method to ensure clean process separation.
        """
        print(f"[Acquisition] Starting on {port} at {baudrate} bps")

        serial_conn = None
        parser = GloveParser()

        # Statistics
        frame_count = 0
        start_time = time.time()
        last_stats_time = start_time
        stats_interval = 1.0  # Report stats every second

        try:
            # Open serial connection
            serial_conn = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
            print(f"[Acquisition] Connected to {port}")

            # Flush any stale data
            serial_conn.reset_input_buffer()

            # Main acquisition loop
            while not stop_event.is_set():
                try:
                    # Read available data
                    if serial_conn.in_waiting > 0:
                        data = serial_conn.read(serial_conn.in_waiting)

                        # Parse into frames
                        frames = parser.add_data(data)

                        # Push frames to queue
                        for frame in frames:
                            timestamp = time.time()
                            frame_data = {
                                'frame': frame,
                                'timestamp': timestamp,
                                'frame_number': frame_count
                            }

                            # Non-blocking put (drop if queue is full)
                            try:
                                frame_queue.put_nowait(frame_data)
                                frame_count += 1
                            except:
                                # Queue full - this shouldn't happen with large queue
                                # but we don't want to block acquisition
                                pass
                    else:
                        # Small sleep to prevent busy-waiting
                        time.sleep(0.0001)  # 100 microseconds

                    # Periodic statistics reporting
                    current_time = time.time()
                    if current_time - last_stats_time >= stats_interval:
                        elapsed = current_time - start_time
                        rate = frame_count / elapsed if elapsed > 0 else 0

                        # Get queue depth (returns -1 on macOS)
                        try:
                            queue_depth = frame_queue.qsize()
                        except NotImplementedError:
                            queue_depth = -1  # Not available on macOS

                        stats = {
                            'frame_count': frame_count,
                            'elapsed_time': elapsed,
                            'capture_rate_hz': rate,
                            'queue_depth': queue_depth,
                            'timestamp': current_time
                        }

                        # Non-blocking stats update
                        try:
                            # Clear old stats first
                            while not stats_queue.empty():
                                try:
                                    stats_queue.get_nowait()
                                except:
                                    break
                            stats_queue.put_nowait(stats)
                        except:
                            pass

                        last_stats_time = current_time

                except serial.SerialException as e:
                    print(f"[Acquisition] Serial error: {e}")
                    break
                except Exception as e:
                    print(f"[Acquisition] Unexpected error: {e}")
                    import traceback
                    traceback.print_exc()

        except serial.SerialException as e:
            print(f"[Acquisition] Failed to open serial port: {e}")
        except Exception as e:
            print(f"[Acquisition] Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            if serial_conn is not None and serial_conn.is_open:
                serial_conn.close()
            print(f"[Acquisition] Stopped. Captured {frame_count} frames")


def main():
    """
    Test standalone acquisition process.

    Usage:
        python acquisition_process.py /dev/cu.usbmodem57640302171
    """
    if len(sys.argv) < 2:
        print("Usage: python acquisition_process.py <serial_port>")
        print("Example: python acquisition_process.py /dev/cu.usbmodem57640302171")
        sys.exit(1)

    port = sys.argv[1]

    print("=" * 60)
    print("Acquisition Process Test")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Baudrate: 921600")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Create and start acquisition
    acq = AcquisitionProcess(port=port)
    acq.start()

    try:
        frame_count = 0
        start_time = time.time()
        last_display = start_time

        while True:
            # Get frame (blocking, 1 second timeout)
            frame_data = acq.get_frame(block=True, timeout=1.0)

            if frame_data is not None:
                frame_count += 1

                # Display statistics every second
                current_time = time.time()
                if current_time - last_display >= 1.0:
                    elapsed = current_time - start_time
                    rate = frame_count / elapsed if elapsed > 0 else 0
                    queue_depth = acq.get_queue_size()

                    # Format queue depth (handle -1 on macOS)
                    queue_str = "N/A" if queue_depth == -1 else f"{queue_depth:4d}"

                    print(f"Frames: {frame_count:6d} | "
                          f"Rate: {rate:6.1f} Hz | "
                          f"Queue: {queue_str:>4s} | "
                          f"Time: {elapsed:6.1f}s")

                    last_display = current_time

            # Check for stats updates
            stats = acq.get_stats(block=False)
            if stats:
                queue_str = "N/A" if stats['queue_depth'] == -1 else str(stats['queue_depth'])
                print(f"[Stats] Capture: {stats['capture_rate_hz']:.1f} Hz | "
                      f"Queue: {queue_str}")

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        acq.stop()

        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Test Results:")
        print(f"  Total frames: {frame_count}")
        print(f"  Duration: {elapsed:.1f} seconds")
        print(f"  Average rate: {frame_count / elapsed:.1f} Hz")
        print("=" * 60)


if __name__ == '__main__':
    main()
