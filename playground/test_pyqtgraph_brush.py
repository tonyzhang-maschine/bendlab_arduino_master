#!/usr/bin/env python3
"""
Test script to verify PyQtGraph brush parameter format
"""

import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph Brush Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        layout.addWidget(self.plot_widget)
        
        # Create scatter plot
        self.scatter = pg.ScatterPlotItem(size=15, pxMode=True)
        self.plot_widget.addItem(self.scatter)
        
        # Test positions
        self.positions = np.array([[i*10, 50] for i in range(10)])
        
        # Test different brush formats
        self.test_format()
        
        # Setup timer to try updating
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_test)
        self.timer.start(1000)
        
    def test_format(self):
        """Test different brush parameter formats."""
        print("\n" + "=" * 60)
        print("Testing PyQtGraph brush parameter formats")
        print("=" * 60)
        
        # Format 1: RGBA array (what we're currently using)
        print("\nFormat 1: RGBA numpy array (uint8)")
        colors = np.zeros((10, 4), dtype=np.uint8)
        for i in range(10):
            colors[i] = [i * 25, 0, 0, 255]  # Red gradient
        print(f"  Shape: {colors.shape}, dtype: {colors.dtype}")
        print(f"  Sample: {colors[0:3]}")
        
        try:
            self.scatter.setData(pos=self.positions, brush=colors)
            print("  ✓ Format accepted")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Format 2: List of tuples
        print("\nFormat 2: List of RGBA tuples")
        colors_list = [(i * 25, 0, 0, 255) for i in range(10)]
        print(f"  Sample: {colors_list[0:3]}")
        
        # Format 3: List of QColor or mkBrush
        print("\nFormat 3: List of pyqtgraph brushes")
        colors_brush = [pg.mkBrush(i * 25, 0, 0, 255) for i in range(10)]
        print(f"  Sample: {type(colors_brush[0])}")
        
        # Try Format 3
        try:
            self.scatter.setData(pos=self.positions, brush=colors_brush)
            print("  ✓ Format accepted - Using this!")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def update_test(self):
        """Update colors to verify updates work."""
        self.counter += 1
        
        # Create gradient that changes over time
        colors_brush = []
        for i in range(10):
            intensity = int((i * 25 + self.counter * 10) % 255)
            colors_brush.append(pg.mkBrush(intensity, 0, 0, 255))
        
        self.scatter.setData(pos=self.positions, brush=colors_brush)
        print(f"Update {self.counter}: Changed colors")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    # Run for a few seconds then quit
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

