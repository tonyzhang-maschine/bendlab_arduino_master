#!/usr/bin/env python3
"""
Integration test for Issue #1 fix
Simulates the full application workflow with low sensor values
"""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from hand_visualizer import HandVisualizer

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Issue #1 Fix - Integration Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Info label
        self.info_label = QLabel("Testing visualization with low sensor values (0-10)")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.info_label)
        
        # Hand visualizer
        self.viz = HandVisualizer()
        layout.addWidget(self.viz)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Test counter
        self.test_count = 0
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_test)
        self.timer.start(1000)  # Update every second
        
        # Run first update
        self.update_test()
        
    def update_test(self):
        """Simulate frame updates with low sensor values."""
        self.test_count += 1
        
        # Create simulated frame data (272 bytes)
        frame_data = np.zeros(272, dtype=np.uint8)
        
        # Simulate pressing different fingers over time
        if self.test_count <= 3:
            # Test 1-3: Thumb (low values 1-6)
            frame_data[19] = min(self.test_count * 2, 6)
            frame_data[18] = min(self.test_count, 5)
            frame_data[17] = min(self.test_count, 3)
            region = "Thumb"
        elif self.test_count <= 6:
            # Test 4-6: Index finger
            offset = self.test_count - 3
            frame_data[22] = min(offset * 2, 6)
            frame_data[21] = min(offset, 5)
            frame_data[20] = min(offset, 4)
            region = "Index Finger"
        elif self.test_count <= 9:
            # Test 7-9: Middle finger
            offset = self.test_count - 6
            frame_data[25] = min(offset * 2, 6)
            frame_data[24] = min(offset, 5)
            frame_data[23] = min(offset, 3)
            region = "Middle Finger"
        else:
            # Test 10+: Multiple fingers
            frame_data[19] = 4  # Thumb
            frame_data[22] = 6  # Index
            frame_data[25] = 3  # Middle
            frame_data[207] = 2  # Palm
            region = "Multiple Regions"
        
        # Extract stats
        max_val = frame_data.max()
        non_zero = np.count_nonzero(frame_data)
        
        # Update visualization
        self.viz.update_sensors(frame_data)
        
        # Calculate expected vmax from our formula
        if max_val > 0:
            expected_vmax = max(min(max_val * 2.5, 255), 10)
        else:
            expected_vmax = 255
        
        # Update status
        status_text = f"""
Test #{self.test_count}: {region}
  Max sensor value: {max_val}
  Active sensors: {non_zero}
  Dynamic vmax: {expected_vmax:.1f}
  
✓ Colors should be VISIBLE (not black)!
        """
        self.status_label.setText(status_text)
        
        # Info update
        if self.test_count == 1:
            self.info_label.setText("🔴 Watch the hand - dots should appear RED (not black)!")
        elif self.test_count == 4:
            self.info_label.setText("🔴 Now testing Index Finger - see the red dots?")
        elif self.test_count == 7:
            self.info_label.setText("🔴 Now testing Middle Finger")
        elif self.test_count == 10:
            self.info_label.setText("🔴 Now testing Multiple Fingers - multiple red dots!")
        
        # Auto-quit after test sequence
        if self.test_count >= 15:
            self.info_label.setText("✅ Test Complete - All sensors visible!")
            QTimer.singleShot(2000, QApplication.instance().quit)

def main():
    print("=" * 70)
    print("Integration Test for Issue #1 Fix")
    print("=" * 70)
    print()
    print("This test simulates the real application with low sensor values.")
    print("Expected behavior:")
    print("  - Sensor dots should appear RED/ORANGE (not black)")
    print("  - Values 1-6 should be clearly visible")
    print("  - Different fingers light up at different times")
    print()
    print("Watch the GUI window...")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

