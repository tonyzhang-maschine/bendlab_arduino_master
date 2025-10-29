#!/usr/bin/env python3
"""
Test integration of new acquisition_process with GUI visualization.
VERSION 2: With aggressive queue draining to minimize latency.
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from acquisition_process import AcquisitionProcess
from hand_visualizer import HandVisualizer


class TestGUIv2(QMainWindow):
    """Minimal GUI to test acquisition_process integration with low latency"""

    def __init__(self, port: str):
        super().__init__()
        self.setWindowTitle("Acquisition Process + GUI Integration Test v2 (Low Latency)")
        self.resize(1200, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)

        # Hand visualizer
        self.visualizer = HandVisualizer()
        layout.addWidget(self.visualizer)

        # Stats labels (side by side)
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Frames: 0 | Rate: 0.0 Hz | Queue: 0")
        self.latency_label = QLabel("Latency: N/A | Frames/update: 0")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.latency_label)
        layout.addLayout(stats_layout)

        # Initialize acquisition process
        self.acq = AcquisitionProcess(port, queue_maxsize=100)  # Smaller queue!
        self.frame_count = 0
        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.last_frame_timestamp = None

        # Start acquisition
        self.acq.start()
        self.status_label.setText(f"✅ Acquisition started on {port}")

        # Update timer (10 Hz GUI update)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)  # 10 Hz

    def update_display(self):
        """Update visualization from acquisition queue"""
        frames_processed = 0
        latest_frame = None
        latest_timestamp = None

        # AGGRESSIVE DRAIN: Empty entire queue, keep only latest frame
        while True:
            frame_data = self.acq.get_frame(block=False)

            if frame_data is None:
                break

            # Keep track of latest
            latest_frame = frame_data['frame']
            latest_timestamp = frame_data['timestamp']
            frames_processed += 1
            self.frame_count += 1

        # Update visualizer with ONLY the latest frame
        if latest_frame is not None:
            self.visualizer.update_sensors(latest_frame)
            self.last_frame_time = time.time()
            self.last_frame_timestamp = latest_timestamp

            # Calculate latency (time from frame capture to display)
            latency = time.time() - latest_timestamp
            self.latency_label.setText(
                f"Latency: {latency*1000:.0f} ms | Frames/update: {frames_processed}"
            )

        # Update stats
        elapsed = time.time() - self.start_time
        rate = self.frame_count / elapsed if elapsed > 0 else 0

        # Get acquisition stats
        stats = self.acq.get_stats(block=False)
        if stats:
            acq_rate = stats.get('capture_rate_hz', 0)
            queue_depth = stats.get('queue_depth', -1)
            queue_str = f"{queue_depth}" if queue_depth >= 0 else "N/A"

            self.stats_label.setText(
                f"Total Frames: {self.frame_count} | "
                f"Avg Rate: {rate:.1f} Hz | "
                f"Acquisition: {acq_rate:.1f} Hz | "
                f"Queue: {queue_str}"
            )
        else:
            self.stats_label.setText(
                f"Frames: {self.frame_count} | Rate: {rate:.1f} Hz | Queue: N/A"
            )

        # Check for complete stall
        stall_time = time.time() - self.last_frame_time
        if stall_time > 2.0 and self.frame_count > 0:
            self.status_label.setText(f"⚠️ Warning: No frames for {stall_time:.1f}s")
        elif frames_processed > 50:
            self.status_label.setText(f"⚠️ Queue backup! Drained {frames_processed} frames this update")
        else:
            self.status_label.setText(f"✅ Running smoothly")

    def closeEvent(self, event):
        """Clean shutdown"""
        print("\nStopping acquisition...")
        self.acq.stop()
        event.accept()


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_gui_integration_v2.py <serial_port>")
        print("Example: python test_gui_integration_v2.py /dev/cu.usbmodem57640302171")
        sys.exit(1)

    port = sys.argv[1]

    print("=" * 60)
    print("Acquisition Process + GUI Integration Test v2")
    print("=" * 60)
    print(f"Port: {port}")
    print("Strategy: AGGRESSIVE QUEUE DRAINING (low latency mode)")
    print("  - Empties entire queue each update")
    print("  - Displays only latest frame")
    print("  - Minimizes visual lag")
    print("Expected: <200ms latency")
    print("=" * 60)
    print()

    app = QApplication(sys.argv)
    window = TestGUIv2(port)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
