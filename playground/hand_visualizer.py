"""
Hand Visualizer - PyQtGraph-based visualization widget for pressure data

Displays hand outline with colored sensor dots representing pressure values.
Uses the documented sensor-to-index mapping from sensor_mapping.py
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from sensor_mapping import SENSOR_REGIONS, get_sensor_count


class HandVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get sensor count from documented mapping
        self.num_sensors = get_sensor_count()  # Should be 136
        self.scale = 100  # Coordinate scale
        
        # Create sensor positions based on documented regions
        self.sensor_positions = self._create_sensor_positions()
        self.sensor_indices = np.array(self._get_ordered_indices(), dtype=np.int32)
        
        # Color mapping (hot colormap: black -> red -> yellow)
        self.vmin = 0
        self.vmax = 255
        
        # Performance optimization: Cache to skip redundant updates
        self.last_colors = None
        self.update_threshold = 1  # Only update if colors change by this much
        
        # Setup UI
        self.setup_ui()
        
    def _create_sensor_positions(self) -> np.ndarray:
        """
        Create approximate visual positions for all 136 sensors based on regions.
        Returns array of shape (136, 2) with (x, y) coordinates.
        """
        positions = []
        
        # Helper function to create finger positions
        def finger_positions(x_base, y_base, count, angle=0):
            angle_rad = np.deg2rad(angle)
            pos = []
            for i in range(count):
                t = i / max(count - 1, 1)
                y = y_base - t * 0.35
                x = x_base + np.sin(angle_rad) * t * 0.08
                # Add width variation
                if i % 3 == 1:
                    x += 0.015
                elif i % 3 == 2:
                    x -= 0.015
                pos.append([x, y])
            return pos
        
        # Little finger (12 sensors) + back (1)
        positions.extend(finger_positions(0.15, 0.8, 12, -10))
        positions.append([0.15, 0.65])  # back
        
        # Ring finger (12 sensors) + back (1)
        positions.extend(finger_positions(0.3, 0.88, 12, -3))
        positions.append([0.3, 0.68])  # back
        
        # Middle finger (12 sensors) + back (1)
        positions.extend(finger_positions(0.45, 0.95, 12, 0))
        positions.append([0.45, 0.75])  # back
        
        # Index finger (12 sensors) + back (1)
        positions.extend(finger_positions(0.6, 0.88, 12, 3))
        positions.append([0.6, 0.68])  # back
        
        # Thumb (12 sensors) + back (1)
        thumb_pos = []
        for i in range(12):
            t = i / 11
            x = 0.75 + t * 0.15
            y = 0.35 + t * 0.25
            if i % 3 == 1:
                y += 0.015
            elif i % 3 == 2:
                y -= 0.015
            thumb_pos.append([x, y])
        positions.extend(thumb_pos)
        positions.append([0.82, 0.5])  # back
        
        # Palm (72 sensors) - grid layout
        palm_rows = 9
        palm_cols = 8
        for row in range(palm_rows):
            for col in range(palm_cols):
                if len(positions) >= self.num_sensors:
                    break
                x = 0.2 + (col / 7) * 0.5
                y = 0.25 + (row / 8) * 0.38
                positions.append([x, y])
            if len(positions) >= self.num_sensors:
                break
        
        return np.array(positions) * self.scale
    
    def _get_ordered_indices(self) -> list:
        """
        Get ordered list of sensor byte indices matching position array.
        Returns list of 136 unique indices.
        """
        indices = []
        seen = set()
        
        # Order should match _create_sensor_positions
        for region_key in ['little_finger', 'little_finger_back',
                          'ring_finger', 'ring_finger_back',
                          'middle_finger', 'middle_finger_back',
                          'index_finger', 'index_finger_back',
                          'thumb', 'thumb_back',
                          'palm']:
            if region_key in SENSOR_REGIONS:
                for idx in SENSOR_REGIONS[region_key]['data_indices']:
                    if idx not in seen:
                        indices.append(idx)
                        seen.add(idx)
        
        return indices
    
    def setup_ui(self):
        """Create the visualization layout."""
        layout = QVBoxLayout(self)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setLabel('bottom', 'X Position')
        self.plot_widget.setLabel('left', 'Y Position')
        self.plot_widget.setTitle('JQ Glove Real-time Pressure Map', color='k', size='14pt')
        
        # Set up axis ranges
        self.plot_widget.setXRange(-5, 105)
        self.plot_widget.setYRange(-5, 105)
        
        # Add hand outline
        self.add_hand_outline()
        
        # Create scatter plot for sensors
        self.sensor_scatter = pg.ScatterPlotItem(
            size=10,
            pen=pg.mkPen(None),
            pxMode=True
        )
        self.plot_widget.addItem(self.sensor_scatter)
        
        # Initialize sensor positions and colors
        colors = np.zeros((self.num_sensors, 4), dtype=np.uint8)
        colors[:, 3] = 255  # Full opacity
        
        self.sensor_scatter.setData(
            pos=self.sensor_positions,
            brush=colors
        )
        
        # Add colorbar
        self.add_colorbar()
        
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
    
    def add_hand_outline(self):
        """Draw simplified hand outline."""
        # Simplified hand outline
        outline_x = np.array([
            25, 70, 70, 75, 80, 88, 95, 95, 88,
            82, 75, 65, 60, 60, 65,
            50, 45, 45, 50,
            35, 30, 30, 35,
            20, 15, 15, 20,
            20, 25, 25
        ])
        
        outline_y = np.array([
            5, 5, 15, 20, 28, 40, 55, 60, 58,
            52, 65, 70, 88, 93, 88,
            70, 95, 100, 95,
            70, 88, 93, 88,
            65, 80, 85, 80,
            60, 18, 5
        ])
        
        self.outline_item = pg.PlotDataItem(
            outline_x, outline_y,
            pen=pg.mkPen('k', width=2),
            connect='all'
        )
        self.plot_widget.addItem(self.outline_item)
    
    def add_colorbar(self):
        """Add colorbar legend to show pressure scale."""
        self.gradient = pg.GradientWidget(orientation='right')
        self.gradient.setMaximumWidth(20)
        
        # Set hot colormap gradient
        self.gradient.restoreState({
            'mode': 'rgb',
            'ticks': [
                (0.0, (0, 0, 0, 255)),      # Black
                (0.33, (128, 0, 0, 255)),   # Dark red
                (0.66, (255, 128, 0, 255)), # Orange
                (1.0, (255, 255, 0, 255))   # Yellow
            ]
        })
    
    def update_sensors(self, frame_data: np.ndarray):
        """
        Update sensor visualization with new frame data.
        
        Args:
            frame_data: 272-byte frame data from glove
        """
        if len(frame_data) < 272:
            return
        
        # Extract values for each sensor using documented indices
        # OPTIMIZED: Use numpy fancy indexing instead of Python loop
        values = frame_data[self.sensor_indices]
        
        # DYNAMIC RANGE ADJUSTMENT: Scale colors based on actual data range
        # This makes low sensor values (0-10) visible instead of nearly black
        max_val = values.max()
        if max_val > 0:
            # Aggressive scaling for visibility:
            # - For low values (< 20): scale to make them bright red/yellow
            # - For higher values: use wider range
            # Formula: Use 2-3x of max value, but clamp between 10 and 255
            dynamic_vmax = max(min(max_val * 2.5, 255), 10)
            self.set_colormap_range(0, dynamic_vmax)
        else:
            # No active sensors, use default range
            self.set_colormap_range(0, 255)
        
        # Convert values to colors
        colors = self.value_to_color(values)
        
        # PERFORMANCE OPTIMIZATION: Only update if colors changed
        # This avoids expensive setData() calls when no visual change
        if self.last_colors is None:
            # First update, always draw
            self.sensor_scatter.setData(
                pos=self.sensor_positions,
                brush=colors
            )
            self.last_colors = colors.copy()
        else:
            # Check if colors changed significantly
            color_diff = np.abs(colors.astype(np.int16) - self.last_colors.astype(np.int16))
            max_change = color_diff[:, :3].max()  # Check RGB channels only
            
            if max_change >= self.update_threshold:
                # Colors changed, update visualization
                self.sensor_scatter.setData(
                    pos=self.sensor_positions,
                    brush=colors
                )
                self.last_colors = colors.copy()
            # else: Skip update, no visual change
    
    def value_to_color(self, values: np.ndarray) -> np.ndarray:
        """
        Convert sensor values to RGBA colors (hot colormap).
        OPTIMIZED: Uses numpy vectorization for 10-20x speed improvement.
        
        Args:
            values: Sensor values (0-255)
            
        Returns:
            Array of shape (N, 4) with RGBA values
        """
        # Normalize values to 0-1 (vectorized)
        normalized = np.clip(values, self.vmin, self.vmax).astype(np.float32)
        normalized = (normalized - self.vmin) / (self.vmax - self.vmin + 1e-7)  # Avoid division by zero
        
        # Create RGBA array
        colors = np.zeros((len(values), 4), dtype=np.uint8)
        colors[:, 3] = 255  # Set alpha to full opacity
        
        # Hot colormap implementation - VECTORIZED
        # Range 1: 0.0 - 0.33 (Black to dark red)
        mask1 = normalized < 0.33
        t1 = normalized[mask1] / 0.33
        colors[mask1, 0] = (128 * t1).astype(np.uint8)
        
        # Range 2: 0.33 - 0.66 (Dark red to orange)
        mask2 = (normalized >= 0.33) & (normalized < 0.66)
        t2 = (normalized[mask2] - 0.33) / 0.33
        colors[mask2, 0] = (128 + 127 * t2).astype(np.uint8)
        colors[mask2, 1] = (128 * t2).astype(np.uint8)
        
        # Range 3: 0.66 - 1.0 (Orange to yellow)
        mask3 = normalized >= 0.66
        t3 = (normalized[mask3] - 0.66) / 0.34
        colors[mask3, 0] = 255
        colors[mask3, 1] = (128 + 127 * t3).astype(np.uint8)
        
        return colors
    
    def set_colormap_range(self, vmin: float, vmax: float):
        """Set the min/max range for color mapping."""
        self.vmin = vmin
        self.vmax = vmax
    
    def clear(self):
        """Reset all sensors to zero (black)."""
        colors = np.zeros((self.num_sensors, 4), dtype=np.uint8)
        colors[:, 3] = 255
        self.sensor_scatter.setData(pos=self.sensor_positions, brush=colors)
        self.last_colors = None  # Reset cache
