#!/usr/bin/env python3
"""
Test script that exactly mimics the real application's scatter plot update
"""

import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer

class ScatterUpdateTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scatter Plot Update Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create plot (exactly like HandVisualizer)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setAspectLocked(True)
        layout.addWidget(self.plot_widget)
        
        # Create scatter plot (exactly like HandVisualizer)
        self.scatter = pg.ScatterPlotItem(
            size=10,
            pen=pg.mkPen(None),
            pxMode=True
        )
        self.plot_widget.addItem(self.scatter)
        
        # Create positions
        self.num_points = 20
        x = np.random.rand(self.num_points) * 100
        y = np.random.rand(self.num_points) * 100
        self.positions = np.column_stack([x, y])
        
        # Initialize with black colors (exactly like HandVisualizer)
        print("\n=== Initialization ===")
        colors = np.zeros((self.num_points, 4), dtype=np.uint8)
        colors[:, 3] = 255  # Full opacity
        print(f"Initial colors: {colors[0]}")
        
        self.scatter.setData(
            pos=self.positions,
            brush=colors
        )
        print("✓ Initialized with black dots")
        
        # Now try to update with non-zero values
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_colors)
        self.timer.start(500)
        
    def update_colors(self):
        """Update colors with increasing intensity."""
        self.counter += 1
        
        print(f"\n=== Update {self.counter} ===")
        
        # Create colors with increasing red intensity
        colors = np.zeros((self.num_points, 4), dtype=np.uint8)
        colors[:, 3] = 255  # Alpha
        
        # Set varying red values
        for i in range(self.num_points):
            intensity = int((i * 12 + self.counter * 20) % 255)
            colors[i, 0] = intensity  # Red channel
        
        print(f"Color range: R={colors[:, 0].min()}-{colors[:, 0].max()}")
        print(f"Sample colors (first 3): {colors[:3]}")
        
        # Update scatter plot (exactly like HandVisualizer.update_sensors)
        self.scatter.setData(
            pos=self.positions,
            brush=colors
        )
        
        print("✓ Called setData() with new colors")
        
        # Try alternative: clear and recreate
        if self.counter == 5:
            print("\n=== Trying alternative method ===")
            self.plot_widget.removeItem(self.scatter)
            self.scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), pxMode=True)
            self.plot_widget.addItem(self.scatter)
            self.scatter.setData(pos=self.positions, brush=colors)
            print("✓ Recreated scatter plot")
        
        if self.counter >= 10:
            print("\n=== Test Complete ===")
            QTimer.singleShot(1000, QApplication.instance().quit)

def main():
    print("=" * 60)
    print("Testing ScatterPlotItem color updates")
    print("Watch the window - dots should change from black to red")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    window = ScatterUpdateTest()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

