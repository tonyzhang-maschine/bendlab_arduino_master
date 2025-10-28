"""
Hand Visualizer - PyQtGraph-based visualization widget for pressure data

Displays hand outline with colored sensor dots representing pressure values.
Uses the documented sensor-to-index mapping from sensor_mapping.py
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from sensor_mapping import (
    SENSOR_REGIONS, 
    get_unique_data_indices, 
    SENSOR_DATA_ASSIGNED,
    get_sensor_by_id,
)
from pressure_calibration import get_calibration


class HandVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get unique data indices for visualization
        # Note: Multiple sensors can share same index (e.g., finger bodies)
        # So we visualize unique data indices (137), not all sensors (162)
        self.sensor_indices = self._get_ordered_indices()
        self.num_sensors = len(self.sensor_indices)  # 137 unique indices
        
        # Create sensor positions from CSV data (real sensor layout!)
        self.sensor_positions = self._create_sensor_positions_from_csv()
        
        # Pressure calibration
        self.calibration = get_calibration()
        self.pressure_unit = 'kPa'  # Default unit
        
        # Color mapping range (will be dynamically adjusted)
        self.vmin = 0
        self.vmax = 10  # Start with reasonable pressure range
        self.colormap = 'viridis'  # Default colormap (much more visible than 'hot')
        
        # Setup UI
        self.setup_ui()
        
    def _create_sensor_positions(self) -> np.ndarray:
        """
        Create approximate visual positions for all unique data indices based on regions.
        Returns array of shape (num_sensors, 2) with (x, y) coordinates.
        Note: num_sensors = 137 (unique data frame indices)
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
    
    def _create_sensor_positions_from_csv(self) -> np.ndarray:
        """
        Create sensor positions using actual X, Y coordinates from CSV.
        
        For data indices that are shared by multiple sensors (finger bodies),
        use the average position of all sensors sharing that index.
        
        Returns array of shape (num_sensors, 2) with (x, y) coordinates.
        """
        if SENSOR_DATA_ASSIGNED is None:
            # Fallback to approximate positions if CSV not available
            print("⚠️  CSV data not available, using approximate positions")
            return self._create_sensor_positions()
        
        # Create mapping: data_frame_index → list of (x, y) positions
        index_to_positions = {}
        
        for _, sensor in SENSOR_DATA_ASSIGNED.iterrows():
            df_index = int(sensor['data_frame_index'])
            x_mm = float(sensor['x_mm'])
            y_mm = float(sensor['y_mm'])
            
            if df_index not in index_to_positions:
                index_to_positions[df_index] = []
            index_to_positions[df_index].append([x_mm, y_mm])
        
        # For each unique data index, compute average position
        # (for shared indices like finger bodies, average all sensor positions)
        positions = []
        for df_index in self.sensor_indices:
            if df_index in index_to_positions:
                # Average position of all sensors sharing this index
                pos_list = index_to_positions[df_index]
                avg_pos = np.mean(pos_list, axis=0)
                positions.append(avg_pos)
            else:
                # Shouldn't happen, but fallback to origin
                print(f"⚠️  Warning: No position found for index {df_index}")
                positions.append([0, 0])
        
        positions = np.array(positions)
        
        # The CSV coordinates are in mm, no need to scale
        # Y-axis flipping is handled by plot range (setYRange reversed)
        # Keep positions as-is from CSV
        
        return positions
    
    def _get_ordered_indices(self) -> list:
        """
        Get ordered list of unique data frame indices matching position array.
        Returns list of 137 unique indices (deduplicated from SENSOR_REGIONS).
        Note: Some indices appear in multiple regions, we keep only unique ones.
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
        self.plot_widget.setLabel('bottom', 'X Position (mm)')
        self.plot_widget.setLabel('left', 'Y Position (mm)')
        
        # Title with pressure unit
        unit_symbol = self.calibration.get_unit_info(self.pressure_unit).get('symbol', self.pressure_unit)
        self.plot_widget.setTitle(f'JQ Glove Real-time Pressure Map ({unit_symbol})', color='k', size='14pt')
        
        # Set up axis ranges based on actual sensor positions
        if len(self.sensor_positions) > 0:
            x_min, x_max = self.sensor_positions[:, 0].min(), self.sensor_positions[:, 0].max()
            y_min, y_max = self.sensor_positions[:, 1].min(), self.sensor_positions[:, 1].max()
            
            # Add 10mm margin on each side
            margin = 10
            self.plot_widget.setXRange(x_min - margin, x_max + margin)
            # Flip Y-axis by setting range in reverse order (higher values at bottom)
            self.plot_widget.setYRange(y_max + margin, y_min - margin)
        else:
            # Fallback ranges (also flipped)
            self.plot_widget.setXRange(-5, 105)
            self.plot_widget.setYRange(105, -5)
        
        # Add hand outline (optional - sensor positions show hand shape)
        # self.add_hand_outline()  # Disabled: Real sensor layout shows hand shape
        
        # Create scatter plot for sensors
        # Using larger dots for better visibility with real sensor layout
        self.sensor_scatter = pg.ScatterPlotItem(
            size=12,
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
        
        # Add colorbar legend
        self.colorbar_label = QLabel()
        self.colorbar_label.setStyleSheet("font-size: 10pt; padding: 5px;")
        self.update_colorbar_label()
        layout.addWidget(self.colorbar_label)
        
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
    
    def update_colorbar_label(self):
        """Update colorbar label with current pressure range, unit, and colormap."""
        unit_info = self.calibration.get_unit_info(self.pressure_unit)
        unit_symbol = unit_info.get('symbol', self.pressure_unit)
        fmt = unit_info.get('format', '{:.2f}')
        
        min_str = fmt.format(self.vmin)
        max_str = fmt.format(self.vmax)
        
        # Colormap descriptions
        colormap_descriptions = {
            'viridis': 'Purple → Blue → Green → Yellow',
            'plasma': 'Purple → Pink → Orange → Yellow',
            'turbo': 'Blue → Cyan → Green → Yellow → Red',
            'YlOrRd': 'Yellow → Orange → Red',
            'hot': 'Black → Red → Orange → Yellow'
        }
        colormap_desc = colormap_descriptions.get(self.colormap, self.colormap)
        
        self.colorbar_label.setText(
            f"Color Scale: {min_str} - {max_str} {unit_symbol} "
            f"({colormap_desc})"
        )
    
    def update_sensors(self, frame_data: np.ndarray):
        """
        Update sensor visualization with new frame data.
        
        Args:
            frame_data: 272-byte frame data from glove
        """
        if len(frame_data) < 272:
            return
        
        # Extract ADC values for each sensor using documented indices
        # Note: idx uses 1-based indexing (1-272), convert to 0-based Python array index
        adc_values = np.zeros(self.num_sensors, dtype=np.uint8)
        for i, idx in enumerate(self.sensor_indices):
            array_index = idx - 1  # Convert 1-based to 0-based
            if array_index >= 0 and array_index < len(frame_data):
                adc_values[i] = frame_data[array_index]
        
        # Convert ADC to pressure values
        pressure_values = self.calibration.adc_to_pressure(adc_values, self.pressure_unit)
        
        # DYNAMIC RANGE ADJUSTMENT: Scale colors based on actual pressure range
        max_pressure = pressure_values.max()
        if max_pressure > 0:
            # Use 2.5x of max pressure for good visibility, with reasonable bounds
            pressure_range_min, pressure_range_max = self.calibration.get_pressure_range(self.pressure_unit)
            
            # Dynamic range: 2.5x current max, but at least 10% of full range
            min_range = pressure_range_max * 0.1
            dynamic_vmax = max(max_pressure * 2.5, min_range)
            
            # Don't exceed full calibration range
            dynamic_vmax = min(dynamic_vmax, pressure_range_max)
            
            self.set_colormap_range(0, dynamic_vmax)
        else:
            # No active sensors, use 10% of full range
            _, max_range = self.calibration.get_pressure_range(self.pressure_unit)
            self.set_colormap_range(0, max_range * 0.1)
        
        # Convert pressure values to colors
        colors = self.value_to_color(pressure_values)
        
        # Update scatter plot
        self.sensor_scatter.setData(
            pos=self.sensor_positions,
            brush=colors
        )
        
        # Update colorbar label with new range
        self.update_colorbar_label()
    
    def value_to_color(self, values: np.ndarray) -> np.ndarray:
        """
        Convert pressure values to RGBA colors using selected colormap.
        
        Args:
            values: Pressure values (in current unit, e.g., kPa)
            
        Returns:
            Array of shape (N, 4) with RGBA values
        """
        # Normalize values to 0-1
        normalized = np.clip(values, self.vmin, self.vmax)
        normalized = (normalized - self.vmin) / (self.vmax - self.vmin)
        
        # Create RGBA array
        colors = np.zeros((len(values), 4), dtype=np.uint8)
        
        # Apply selected colormap
        if self.colormap == 'viridis':
            colors = self._colormap_viridis(normalized)
        elif self.colormap == 'plasma':
            colors = self._colormap_plasma(normalized)
        elif self.colormap == 'turbo':
            colors = self._colormap_turbo(normalized)
        elif self.colormap == 'YlOrRd':
            colors = self._colormap_ylorrd(normalized)
        elif self.colormap == 'hot':
            colors = self._colormap_hot(normalized)
        else:
            # Fallback to viridis
            colors = self._colormap_viridis(normalized)
        
        return colors
    
    def _colormap_viridis(self, normalized: np.ndarray) -> np.ndarray:
        """Viridis colormap: Purple → Blue → Green → Yellow (perceptually uniform)"""
        colors = np.zeros((len(normalized), 4), dtype=np.uint8)
        for i, val in enumerate(normalized):
            if val < 0.25:
                t = val / 0.25
                # Dark purple to purple
                colors[i] = [int(68 + (59 - 68) * t), int(1 + (82 - 1) * t), int(84 + (139 - 84) * t), 255]
            elif val < 0.5:
                t = (val - 0.25) / 0.25
                # Purple to teal
                colors[i] = [int(59 + (33 - 59) * t), int(82 + (144 - 82) * t), int(139 + (140 - 139) * t), 255]
            elif val < 0.75:
                t = (val - 0.5) / 0.25
                # Teal to green
                colors[i] = [int(33 + (94 - 33) * t), int(144 + (201 - 144) * t), int(140 + (98 - 140) * t), 255]
            else:
                t = (val - 0.75) / 0.25
                # Green to yellow
                colors[i] = [int(94 + (253 - 94) * t), int(201 + (231 - 201) * t), int(98 + (37 - 98) * t), 255]
        return colors
    
    def _colormap_plasma(self, normalized: np.ndarray) -> np.ndarray:
        """Plasma colormap: Purple → Pink → Orange → Yellow (high contrast)"""
        colors = np.zeros((len(normalized), 4), dtype=np.uint8)
        for i, val in enumerate(normalized):
            if val < 0.25:
                t = val / 0.25
                # Dark purple to purple
                colors[i] = [int(13 + (126 - 13) * t), int(8 + (3 - 8) * t), int(135 + (168 - 135) * t), 255]
            elif val < 0.5:
                t = (val - 0.25) / 0.25
                # Purple to magenta
                colors[i] = [int(126 + (204 - 126) * t), int(3 + (71 - 3) * t), int(168 + (120 - 168) * t), 255]
            elif val < 0.75:
                t = (val - 0.5) / 0.25
                # Magenta to orange
                colors[i] = [int(204 + (240 - 204) * t), int(71 + (142 - 71) * t), int(120 + (53 - 120) * t), 255]
            else:
                t = (val - 0.75) / 0.25
                # Orange to yellow
                colors[i] = [int(240 + (240 - 240) * t), int(142 + (249 - 142) * t), int(53 + (33 - 53) * t), 255]
        return colors
    
    def _colormap_turbo(self, normalized: np.ndarray) -> np.ndarray:
        """Turbo colormap: Blue → Cyan → Green → Yellow → Red (improved jet)"""
        colors = np.zeros((len(normalized), 4), dtype=np.uint8)
        for i, val in enumerate(normalized):
            if val < 0.2:
                t = val / 0.2
                # Blue to cyan
                colors[i] = [int(48 + (34 - 48) * t), int(18 + (167 - 18) * t), int(59 + (227 - 59) * t), 255]
            elif val < 0.4:
                t = (val - 0.2) / 0.2
                # Cyan to green
                colors[i] = [int(34 + (31 - 34) * t), int(167 + (228 - 167) * t), int(227 + (139 - 227) * t), 255]
            elif val < 0.6:
                t = (val - 0.4) / 0.2
                # Green to yellow
                colors[i] = [int(31 + (189 - 31) * t), int(228 + (230 - 228) * t), int(139 + (43 - 139) * t), 255]
            elif val < 0.8:
                t = (val - 0.6) / 0.2
                # Yellow to orange
                colors[i] = [int(189 + (249 - 189) * t), int(230 + (152 - 230) * t), int(43 + (40 - 43) * t), 255]
            else:
                t = (val - 0.8) / 0.2
                # Orange to red
                colors[i] = [int(249 + (122 - 249) * t), int(152 + (4 - 152) * t), int(40 + (3 - 40) * t), 255]
        return colors
    
    def _colormap_ylorrd(self, normalized: np.ndarray) -> np.ndarray:
        """Yellow-Orange-Red colormap: Bright yellow → Orange → Red (high visibility)"""
        colors = np.zeros((len(normalized), 4), dtype=np.uint8)
        for i, val in enumerate(normalized):
            if val < 0.5:
                t = val / 0.5
                # Bright yellow to orange
                colors[i] = [int(255), int(255 - (255 - 178) * t), int(178 - (178 - 0) * t), 255]
            else:
                t = (val - 0.5) / 0.5
                # Orange to dark red
                colors[i] = [int(255 - (255 - 128) * t), int(178 - (178 - 0) * t), int(0), 255]
        return colors
    
    def _colormap_hot(self, normalized: np.ndarray) -> np.ndarray:
        """Hot colormap: Black → Red → Orange → Yellow (original)"""
        colors = np.zeros((len(normalized), 4), dtype=np.uint8)
        for i, val in enumerate(normalized):
            if val < 0.33:
                t = val / 0.33
                # Black to dark red
                colors[i] = [int(128 * t), 0, 0, 255]
            elif val < 0.66:
                t = (val - 0.33) / 0.33
                # Dark red to orange
                colors[i] = [128 + int(127 * t), int(128 * t), 0, 255]
            else:
                t = (val - 0.66) / 0.34
                # Orange to yellow
                colors[i] = [255, 128 + int(127 * t), 0, 255]
        return colors
    
    def set_colormap_range(self, vmin: float, vmax: float):
        """Set the min/max range for color mapping."""
        self.vmin = vmin
        self.vmax = max(vmax, vmin + 0.01)  # Prevent division by zero
    
    def set_pressure_unit(self, unit: str):
        """
        Change the pressure unit for display.
        
        Args:
            unit: Pressure unit ('kPa', 'mmHg', or 'N/cm2')
        """
        self.pressure_unit = unit
        
        # Update plot title
        unit_symbol = self.calibration.get_unit_info(unit).get('symbol', unit)
        self.plot_widget.setTitle(f'JQ Glove Real-time Pressure Map ({unit_symbol})', color='k', size='14pt')
        
        # Reset color range to 10% of new unit's full range
        _, max_range = self.calibration.get_pressure_range(unit)
        self.set_colormap_range(0, max_range * 0.1)
        
        # Update colorbar
        self.update_colorbar_label()
    
    def set_colormap(self, colormap: str):
        """
        Change the colormap for visualization.
        
        Args:
            colormap: Colormap name ('viridis', 'plasma', 'turbo', 'YlOrRd', 'hot')
        """
        valid_colormaps = ['viridis', 'plasma', 'turbo', 'YlOrRd', 'hot']
        if colormap in valid_colormaps:
            self.colormap = colormap
            self.update_colorbar_label()
        else:
            print(f"Warning: Unknown colormap '{colormap}', using 'viridis'")
            self.colormap = 'viridis'
    
    def clear(self):
        """Reset all sensors to zero (black)."""
        colors = np.zeros((self.num_sensors, 4), dtype=np.uint8)
        colors[:, 3] = 255
        self.sensor_scatter.setData(pos=self.sensor_positions, brush=colors)
