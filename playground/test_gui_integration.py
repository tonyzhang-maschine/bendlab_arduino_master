#!/usr/bin/env python3
"""
Test integration of new acquisition_process with GUI visualization.
This is a simplified test to verify the multiprocessing acquisition works with PyQtGraph.
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from acquisition_process import AcquisitionProcess
from hand_visualizer import HandVisualizer


class TestGUI(QMainWindow):
    """Minimal GUI to test acquisition_process integration"""

    def __init__(self, port: str):
        super().__init__()
        self.setWindowTitle("Acquisition Process + GUI Integration Test")
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

        # Stats label
        self.stats_label = QLabel("Frames: 0 | Rate: 0.0 Hz | Queue: 0")
        layout.addWidget(self.stats_label)

        # Initialize acquisition process
        self.acq = AcquisitionProcess(port)
        self.frame_count = 0
        self.start_time = time.time()
        self.last_frame_time = time.time()

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

        # Process multiple frames if available (catch up if behind)
        while frames_processed < 5:  # Process up to 5 frames per update
            frame_data = self.acq.get_frame(block=False)

            if frame_data is None:
                break

            # Update visualizer
            frame = frame_data['frame']
            self.visualizer.update_sensors(frame)

            self.frame_count += 1
            frames_processed += 1
            self.last_frame_time = time.time()

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
                f"GUI Frames: {self.frame_count} | "
                f"GUI Rate: {rate:.1f} Hz | "
                f"Acquisition: {acq_rate:.1f} Hz | "
                f"Queue: {queue_str}"
            )
        else:
            self.stats_label.setText(
                f"Frames: {self.frame_count} | Rate: {rate:.1f} Hz | Queue: N/A"
            )

        # Check for lag
        lag = time.time() - self.last_frame_time
        if lag > 1.0 and self.frame_count > 0:
            self.status_label.setText(f"⚠️ Warning: No frames for {lag:.1f}s")

    def closeEvent(self, event):
        """Clean shutdown"""
        print("\nStopping acquisition...")
        self.acq.stop()
        event.accept()


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_gui_integration.py <serial_port>")
        print("Example: python test_gui_integration.py /dev/cu.usbmodem57640302171")
        sys.exit(1)

    port = sys.argv[1]

    print("=" * 60)
    print("Acquisition Process + GUI Integration Test")
    print("=" * 60)
    print(f"Port: {port}")
    print("Testing: AcquisitionProcess → Queue → GUI Display")
    print("Expected: 200 Hz acquisition, 10 Hz GUI update")
    print("=" * 60)
    print()

    app = QApplication(sys.argv)
    window = TestGUI(port)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
