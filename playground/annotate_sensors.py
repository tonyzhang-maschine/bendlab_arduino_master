#!/usr/bin/env python3
"""
Interactive Sensor Annotation Tool
Allows visual selection and labeling of glove sensors by region
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QListWidget, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QColor
import pyqtgraph as pg


# Region definitions
REGIONS = {
    'thumb': {'name': 'Thumb (大拇指)', 'color': (255, 100, 100, 200)},
    'index': {'name': 'Index (食指)', 'color': (100, 255, 100, 200)},
    'middle': {'name': 'Middle (中指)', 'color': (100, 100, 255, 200)},
    'ring': {'name': 'Ring (无名指)', 'color': (255, 255, 100, 200)},
    'little': {'name': 'Little (小拇指)', 'color': (255, 100, 255, 200)},
    'palm': {'name': 'Palm (手掌)', 'color': (100, 255, 255, 200)},
    'unassigned': {'name': 'Unassigned', 'color': (150, 150, 150, 200)}
}


class SelectableScatterPlotItem(pg.ScatterPlotItem):
    """Enhanced scatter plot with selection support"""
    
    selection_changed = pyqtSignal(list)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_indices = set()
        self.is_selecting = False
        self.selection_start = None
        
    def select_points(self, indices, clear=True):
        """Select points by indices"""
        if clear:
            self.selected_indices = set(indices)
        else:
            self.selected_indices.update(indices)
        self.selection_changed.emit(list(self.selected_indices))
        self.update_selection_visual()
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_indices.clear()
        self.selection_changed.emit([])
        self.update_selection_visual()
    
    def update_selection_visual(self):
        """Update visual appearance of selected points"""
        # This will be handled by the parent widget updating sizes
        pass


class SensorAnnotationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glove Sensor Annotation Tool")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data
        self.df = None
        self.sensor_positions = None
        self.sensor_ids = None
        self.assignments = {}  # sensor_id -> region
        self.history = []  # For undo
        
        # Current state
        self.current_region = 'thumb'
        self.selection_mode = 'rectangle'  # 'rectangle', 'lasso', 'click'
        
        # Selection state
        self.is_selecting = False
        self.selection_start = None
        self.selection_rect = None
        self.lasso_points = []
        self.lasso_line = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Visualization
        left_panel = self.create_visualization_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Controls
        right_panel = self.create_control_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 3)  # Visualization gets more space
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
    def create_visualization_panel(self):
        """Create the main visualization area"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Sensor Map - Click and drag to select sensors")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setLabel('bottom', 'X Position (mm)')
        self.plot_widget.setLabel('left', 'Y Position (mm)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Enable mouse interaction
        self.plot_widget.scene().sigMouseClicked.connect(self.on_plot_clicked)
        self.plot_widget.scene().sigMouseMoved.connect(self.on_mouse_moved)
        
        layout.addWidget(self.plot_widget)
        
        # Status bar
        self.status_label = QLabel("Load a CSV file to begin")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        return panel
    
    def create_control_panel(self):
        """Create the control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File operations
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout()
        
        load_btn = QPushButton("Load CSV")
        load_btn.clicked.connect(self.load_csv)
        file_layout.addWidget(load_btn)
        
        save_btn = QPushButton("Save Annotated CSV")
        save_btn.clicked.connect(self.save_csv)
        file_layout.addWidget(save_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Selection mode
        selection_group = QGroupBox("Selection Mode")
        selection_layout = QVBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Rectangle', 'Lasso', 'Click (single)', 'Click (multi)'])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        selection_layout.addWidget(self.mode_combo)
        
        clear_sel_btn = QPushButton("Clear Selection")
        clear_sel_btn.clicked.connect(self.clear_selection)
        selection_layout.addWidget(clear_sel_btn)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # Region assignment
        region_group = QGroupBox("Assign Selected to Region")
        region_layout = QGridLayout()
        
        row = 0
        for region_key, region_info in REGIONS.items():
            if region_key == 'unassigned':
                continue
            
            btn = QPushButton(region_info['name'])
            color = QColor(*region_info['color'])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({color.red()}, {color.green()}, {color.blue()}, 180);
                    border: 2px solid #333;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 3px solid #000;
                }}
            """)
            btn.clicked.connect(lambda checked, r=region_key: self.assign_region(r))
            region_layout.addWidget(btn, row // 2, row % 2)
            row += 1
        
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_list = QListWidget()
        stats_layout.addWidget(self.stats_list)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Actions
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout()
        
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)
        action_layout.addWidget(undo_btn)
        
        clear_all_btn = QPushButton("Clear All Assignments")
        clear_all_btn.clicked.connect(self.clear_all_assignments)
        action_layout.addWidget(clear_all_btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        return panel
    
    def load_csv(self):
        """Load sensor CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Sensor CSV",
            str(Path(__file__).parent),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.df = pd.read_csv(file_path)
            
            # Validate columns
            required_cols = ['sensor_id', 'x_mm', 'y_mm']
            if not all(col in self.df.columns for col in required_cols):
                raise ValueError(f"CSV must contain columns: {required_cols}")
            
            # Load existing region assignments if present
            if 'region' in self.df.columns:
                for _, row in self.df.iterrows():
                    self.assignments[row['sensor_id']] = row['region']
            else:
                # Initialize all as unassigned
                for sensor_id in self.df['sensor_id']:
                    self.assignments[sensor_id] = 'unassigned'
            
            self.sensor_positions = self.df[['x_mm', 'y_mm']].values
            self.sensor_ids = self.df['sensor_id'].values
            
            self.plot_sensors()
            self.update_statistics()
            self.status_label.setText(f"Loaded {len(self.df)} sensors from {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV:\n{str(e)}")
    
    def plot_sensors(self):
        """Plot all sensors with colors based on region assignment"""
        if self.df is None:
            return
        
        self.plot_widget.clear()
        
        # Create scatter plot for each region
        self.scatter_items = {}
        
        for region_key, region_info in REGIONS.items():
            # Get sensors assigned to this region
            sensor_mask = [self.assignments.get(sid, 'unassigned') == region_key 
                          for sid in self.sensor_ids]
            
            if not any(sensor_mask):
                continue
            
            positions = self.sensor_positions[sensor_mask]
            ids = self.sensor_ids[sensor_mask]
            
            # Create scatter plot
            scatter = pg.ScatterPlotItem(
                pos=positions,
                size=12,
                pen=pg.mkPen('k', width=1),
                brush=pg.mkBrush(*region_info['color']),
                hoverable=True,
                hoverSize=15,
                tip=None
            )
            
            # Add tooltips with sensor IDs
            scatter.sigClicked.connect(self.on_point_clicked)
            
            self.plot_widget.addItem(scatter)
            self.scatter_items[region_key] = scatter
        
        # Add text labels for sensor IDs (every 5th sensor to avoid clutter)
        for i, (sid, pos) in enumerate(zip(self.sensor_ids, self.sensor_positions)):
            if i % 5 == 0:
                text = pg.TextItem(str(sid), anchor=(0.5, 0.5), color='k')
                text.setPos(pos[0], pos[1])
                self.plot_widget.addItem(text)
        
        # Auto-range
        self.plot_widget.autoRange()
    
    def on_plot_clicked(self, event):
        """Handle plot click events"""
        if self.df is None:
            return
        
        mode_text = self.mode_combo.currentText()
        pos = event.scenePos()
        
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            
            if mode_text == 'Rectangle':
                if event.button() == Qt.LeftButton:
                    if not self.is_selecting:
                        # Start selection
                        self.is_selecting = True
                        self.selection_start = mouse_point
                        self.selection_rect = pg.RectROI([mouse_point.x(), mouse_point.y()], 
                                                         [1, 1], 
                                                         pen='r')
                        self.plot_widget.addItem(self.selection_rect)
                    else:
                        # End selection
                        self.finish_rectangle_selection()
            
            elif mode_text == 'Lasso':
                if event.button() == Qt.LeftButton:
                    if not self.is_selecting:
                        # Start lasso
                        self.is_selecting = True
                        self.lasso_points = [(mouse_point.x(), mouse_point.y())]
                        self.lasso_line = pg.PlotDataItem(pen='r', width=2)
                        self.plot_widget.addItem(self.lasso_line)
                    else:
                        # End lasso
                        self.finish_lasso_selection()
            
            elif 'Click' in mode_text:
                # Find nearest sensor
                nearest_idx = self.find_nearest_sensor(mouse_point.x(), mouse_point.y())
                if nearest_idx is not None:
                    if 'multi' in mode_text.lower():
                        # Toggle selection
                        self.toggle_sensor_selection(nearest_idx)
                    else:
                        # Single selection
                        self.select_sensors([nearest_idx])
    
    def on_mouse_moved(self, pos):
        """Handle mouse movement for drag operations"""
        if self.df is None or not self.is_selecting:
            return
        
        mode_text = self.mode_combo.currentText()
        
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            
            if mode_text == 'Rectangle' and self.selection_rect is not None:
                # Update rectangle
                width = mouse_point.x() - self.selection_start.x()
                height = mouse_point.y() - self.selection_start.y()
                self.selection_rect.setSize([width, height])
            
            elif mode_text == 'Lasso' and self.lasso_line is not None:
                # Add point to lasso
                self.lasso_points.append((mouse_point.x(), mouse_point.y()))
                x_coords = [p[0] for p in self.lasso_points]
                y_coords = [p[1] for p in self.lasso_points]
                self.lasso_line.setData(x_coords, y_coords)
    
    def finish_rectangle_selection(self):
        """Complete rectangle selection"""
        if self.selection_rect is None:
            return
        
        # Get rectangle bounds
        rect_pos = self.selection_rect.pos()
        rect_size = self.selection_rect.size()
        
        x_min = rect_pos.x()
        y_min = rect_pos.y()
        x_max = x_min + rect_size[0]
        y_max = y_min + rect_size[1]
        
        # Find sensors in rectangle
        selected = []
        for i, pos in enumerate(self.sensor_positions):
            if (x_min <= pos[0] <= x_max) and (y_min <= pos[1] <= y_max):
                selected.append(i)
        
        self.select_sensors(selected)
        
        # Clean up
        self.plot_widget.removeItem(self.selection_rect)
        self.selection_rect = None
        self.is_selecting = False
    
    def finish_lasso_selection(self):
        """Complete lasso selection"""
        if len(self.lasso_points) < 3:
            self.cleanup_lasso()
            return
        
        # Close the lasso
        self.lasso_points.append(self.lasso_points[0])
        
        # Find sensors inside lasso using point-in-polygon test
        selected = []
        for i, pos in enumerate(self.sensor_positions):
            if self.point_in_polygon(pos[0], pos[1], self.lasso_points):
                selected.append(i)
        
        self.select_sensors(selected)
        self.cleanup_lasso()
    
    def cleanup_lasso(self):
        """Clean up lasso drawing"""
        if self.lasso_line is not None:
            self.plot_widget.removeItem(self.lasso_line)
            self.lasso_line = None
        self.lasso_points = []
        self.is_selecting = False
    
    def point_in_polygon(self, x, y, poly_points):
        """Check if point is inside polygon using ray casting"""
        n = len(poly_points)
        inside = False
        
        p1x, p1y = poly_points[0]
        for i in range(1, n + 1):
            p2x, p2y = poly_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def find_nearest_sensor(self, x, y, max_distance=10):
        """Find nearest sensor to click point"""
        distances = np.sqrt((self.sensor_positions[:, 0] - x)**2 + 
                           (self.sensor_positions[:, 1] - y)**2)
        nearest_idx = np.argmin(distances)
        
        if distances[nearest_idx] < max_distance:
            return nearest_idx
        return None
    
    def on_point_clicked(self, item, points):
        """Handle direct point clicks"""
        # This is called when clicking on a scatter point
        pass
    
    def select_sensors(self, indices):
        """Select sensors by array indices"""
        self.selected_sensors = indices
        self.highlight_selection()
        self.status_label.setText(f"Selected {len(indices)} sensor(s)")
    
    def toggle_sensor_selection(self, index):
        """Toggle sensor selection"""
        if not hasattr(self, 'selected_sensors'):
            self.selected_sensors = []
        
        if index in self.selected_sensors:
            self.selected_sensors.remove(index)
        else:
            self.selected_sensors.append(index)
        
        self.highlight_selection()
        self.status_label.setText(f"Selected {len(self.selected_sensors)} sensor(s)")
    
    def highlight_selection(self):
        """Highlight selected sensors"""
        if not hasattr(self, 'selected_sensors') or not self.selected_sensors:
            # Remove existing highlight
            if hasattr(self, 'highlight_item') and self.highlight_item is not None:
                self.plot_widget.removeItem(self.highlight_item)
                self.highlight_item = None
            return
        
        # Remove old highlight
        if hasattr(self, 'highlight_item') and self.highlight_item is not None:
            self.plot_widget.removeItem(self.highlight_item)
        
        # Add new highlight
        selected_positions = self.sensor_positions[self.selected_sensors]
        self.highlight_item = pg.ScatterPlotItem(
            pos=selected_positions,
            size=20,
            pen=pg.mkPen('r', width=3),
            brush=None,
            symbol='o'
        )
        self.plot_widget.addItem(self.highlight_item)
    
    def clear_selection(self):
        """Clear current selection"""
        self.selected_sensors = []
        self.highlight_selection()
        self.status_label.setText("Selection cleared")
    
    def assign_region(self, region):
        """Assign selected sensors to region"""
        if not hasattr(self, 'selected_sensors') or not self.selected_sensors:
            QMessageBox.warning(self, "No Selection", "Please select sensors first")
            return
        
        # Save to history for undo
        self.history.append(dict(self.assignments))
        
        # Assign region
        for idx in self.selected_sensors:
            sensor_id = self.sensor_ids[idx]
            self.assignments[sensor_id] = region
        
        # Update display
        self.plot_sensors()
        self.update_statistics()
        self.clear_selection()
        
        region_name = REGIONS[region]['name']
        self.status_label.setText(f"Assigned {len(self.selected_sensors)} sensor(s) to {region_name}")
    
    def update_statistics(self):
        """Update statistics display"""
        self.stats_list.clear()
        
        # Count sensors per region
        counts = {}
        for region_key in REGIONS.keys():
            counts[region_key] = sum(1 for r in self.assignments.values() if r == region_key)
        
        # Display
        total = len(self.assignments)
        self.stats_list.addItem(f"Total Sensors: {total}")
        self.stats_list.addItem("")
        
        for region_key, region_info in REGIONS.items():
            count = counts[region_key]
            pct = (count / total * 100) if total > 0 else 0
            self.stats_list.addItem(f"{region_info['name']}: {count} ({pct:.1f}%)")
    
    def undo(self):
        """Undo last assignment"""
        if not self.history:
            QMessageBox.information(self, "Undo", "Nothing to undo")
            return
        
        self.assignments = self.history.pop()
        self.plot_sensors()
        self.update_statistics()
        self.status_label.setText("Undid last assignment")
    
    def clear_all_assignments(self):
        """Clear all region assignments"""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Are you sure you want to clear all region assignments?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history.append(dict(self.assignments))
            for sensor_id in self.assignments:
                self.assignments[sensor_id] = 'unassigned'
            
            self.plot_sensors()
            self.update_statistics()
            self.status_label.setText("Cleared all assignments")
    
    def on_mode_changed(self, mode_text):
        """Handle selection mode change"""
        self.status_label.setText(f"Selection mode: {mode_text}")
    
    def save_csv(self):
        """Save annotated CSV file"""
        if self.df is None:
            QMessageBox.warning(self, "No Data", "Please load a CSV file first")
            return
        
        # Check for unassigned sensors
        unassigned_count = sum(1 for r in self.assignments.values() if r == 'unassigned')
        if unassigned_count > 0:
            reply = QMessageBox.question(
                self,
                "Unassigned Sensors",
                f"{unassigned_count} sensors are still unassigned. Save anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Annotated CSV",
            str(Path(__file__).parent / "glove_sensor_map_annotated.csv"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            # Add region column to dataframe
            self.df['region'] = self.df['sensor_id'].map(self.assignments)
            
            # Save
            self.df.to_csv(file_path, index=False)
            
            QMessageBox.information(
                self,
                "Success",
                f"Saved annotated CSV to:\n{file_path}"
            )
            self.status_label.setText(f"Saved to {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save CSV:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SensorAnnotationTool()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

