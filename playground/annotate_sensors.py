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
    QGroupBox, QGridLayout, QListWidget, QSplitter, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QColor, QIntValidator
import pyqtgraph as pg


# Region definitions - Separated into tips and bodies
REGIONS = {
    # Thumb
    'thumb_tip': {'name': 'Thumb Tip (大拇指尖)', 'color': (255, 80, 80, 200)},
    'thumb_body': {'name': 'Thumb Body (大拇指身)', 'color': (200, 100, 100, 200)},
    
    # Index finger
    'index_tip': {'name': 'Index Tip (食指尖)', 'color': (80, 255, 80, 200)},
    'index_body': {'name': 'Index Body (食指身)', 'color': (100, 200, 100, 200)},
    
    # Middle finger
    'middle_tip': {'name': 'Middle Tip (中指尖)', 'color': (80, 80, 255, 200)},
    'middle_body': {'name': 'Middle Body (中指身)', 'color': (100, 100, 200, 200)},
    
    # Ring finger
    'ring_tip': {'name': 'Ring Tip (无名指尖)', 'color': (255, 255, 80, 200)},
    'ring_body': {'name': 'Ring Body (无名指身)', 'color': (200, 200, 100, 200)},
    
    # Little finger
    'little_tip': {'name': 'Little Tip (小拇指尖)', 'color': (255, 80, 255, 200)},
    'little_body': {'name': 'Little Body (小拇指身)', 'color': (200, 100, 200, 200)},
    
    # Palm
    'palm': {'name': 'Palm (手掌)', 'color': (100, 255, 255, 200)},
    
    # Unassigned
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
        self.dataframe_indices = {}  # sensor_id -> data_frame_index
        self.history = []  # For undo

        # Inspector state
        self.selected_sensor_id = None  # Currently inspected sensor
        
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

        # Sensor Inspector Panel
        inspector_group = QGroupBox("Sensor Inspector")
        inspector_layout = QVBoxLayout()

        # Info labels
        self.inspector_sensor_id_label = QLabel("Sensor ID: --")
        self.inspector_position_label = QLabel("Position: --")
        self.inspector_region_label = QLabel("Region: --")

        inspector_layout.addWidget(self.inspector_sensor_id_label)
        inspector_layout.addWidget(self.inspector_position_label)
        inspector_layout.addWidget(self.inspector_region_label)

        # Add spacing
        inspector_layout.addSpacing(10)

        # Data frame index editor
        index_label = QLabel("Data Frame Index:")
        index_label.setStyleSheet("font-weight: bold;")
        inspector_layout.addWidget(index_label)

        # Input field with validator
        self.inspector_index_input = QLineEdit()
        self.inspector_index_input.setPlaceholderText("Enter index (-1 to 255)")
        validator = QIntValidator(-1, 255)
        self.inspector_index_input.setValidator(validator)
        inspector_layout.addWidget(self.inspector_index_input)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.inspector_update_btn = QPushButton("Update")
        self.inspector_update_btn.clicked.connect(self.on_index_update_clicked)
        buttons_layout.addWidget(self.inspector_update_btn)

        self.inspector_unassign_btn = QPushButton("Set Unassigned (-1)")
        self.inspector_unassign_btn.clicked.connect(self.on_set_unassigned_clicked)
        buttons_layout.addWidget(self.inspector_unassign_btn)

        inspector_layout.addLayout(buttons_layout)

        # Status label
        self.inspector_status_label = QLabel("")
        self.inspector_status_label.setWordWrap(True)
        self.inspector_status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        inspector_layout.addWidget(self.inspector_status_label)

        inspector_group.setLayout(inspector_layout)
        layout.addWidget(inspector_group)

        # Initially disable inspector (no sensor selected)
        self.set_inspector_enabled(False)

        # Region assignment - Organized by finger
        region_group = QGroupBox("Assign Selected to Region")
        region_layout = QVBoxLayout()
        
        # Helper function to create finger button pair
        def create_finger_buttons(finger_name, tip_key, body_key):
            finger_widget = QWidget()
            finger_layout = QHBoxLayout(finger_widget)
            finger_layout.setContentsMargins(0, 0, 0, 0)
            
            # Tip button
            tip_btn = QPushButton(REGIONS[tip_key]['name'])
            tip_color = QColor(*REGIONS[tip_key]['color'])
            tip_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({tip_color.red()}, {tip_color.green()}, {tip_color.blue()}, 180);
                    border: 2px solid #333;
                    padding: 6px;
                    font-size: 10pt;
                }}
                QPushButton:hover {{
                    border: 3px solid #000;
                }}
            """)
            tip_btn.clicked.connect(lambda: self.assign_region(tip_key))
            
            # Body button
            body_btn = QPushButton(REGIONS[body_key]['name'])
            body_color = QColor(*REGIONS[body_key]['color'])
            body_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({body_color.red()}, {body_color.green()}, {body_color.blue()}, 180);
                    border: 2px solid #333;
                    padding: 6px;
                    font-size: 10pt;
                }}
                QPushButton:hover {{
                    border: 3px solid #000;
                }}
            """)
            body_btn.clicked.connect(lambda: self.assign_region(body_key))
            
            finger_layout.addWidget(tip_btn)
            finger_layout.addWidget(body_btn)
            return finger_widget
        
        # Add finger buttons (tip + body for each)
        region_layout.addWidget(create_finger_buttons("Thumb", "thumb_tip", "thumb_body"))
        region_layout.addWidget(create_finger_buttons("Index", "index_tip", "index_body"))
        region_layout.addWidget(create_finger_buttons("Middle", "middle_tip", "middle_body"))
        region_layout.addWidget(create_finger_buttons("Ring", "ring_tip", "ring_body"))
        region_layout.addWidget(create_finger_buttons("Little", "little_tip", "little_body"))
        
        # Palm button (full width)
        palm_btn = QPushButton(REGIONS['palm']['name'])
        palm_color = QColor(*REGIONS['palm']['color'])
        palm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({palm_color.red()}, {palm_color.green()}, {palm_color.blue()}, 180);
                border: 2px solid #333;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border: 3px solid #000;
            }}
        """)
        palm_btn.clicked.connect(lambda: self.assign_region('palm'))
        region_layout.addWidget(palm_btn)
        
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

            # Load existing data_frame_index values if present
            if 'data_frame_index' in self.df.columns:
                for _, row in self.df.iterrows():
                    self.dataframe_indices[row['sensor_id']] = int(row['data_frame_index'])
            else:
                # Initialize all as -1 (unassigned)
                for sensor_id in self.df['sensor_id']:
                    self.dataframe_indices[sensor_id] = -1
            
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

        # Add visual markers for sensors with data_frame_index == -1
        unassigned_indices_positions = []
        for i, sid in enumerate(self.sensor_ids):
            if self.dataframe_indices.get(sid, -1) == -1:
                unassigned_indices_positions.append(self.sensor_positions[i])

        if unassigned_indices_positions:
            # Add special markers (hollow squares) for unassigned data_frame_index
            unassigned_scatter = pg.ScatterPlotItem(
                pos=unassigned_indices_positions,
                size=18,
                pen=pg.mkPen('r', width=2, style=Qt.DashLine),
                brush=None,
                symbol='s',  # square
                pxMode=True
            )
            self.plot_widget.addItem(unassigned_scatter)

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
                        # Update inspector for single-click mode
                        self.update_inspector(nearest_idx)
    
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
        self.save_state_to_history()

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

        state = self.history.pop()
        self.assignments = state['assignments']
        self.dataframe_indices = state['dataframe_indices']
        self.plot_sensors()
        self.update_statistics()

        # Refresh inspector if a sensor is currently selected
        if self.selected_sensor_id is not None:
            # Find the sensor index
            sensor_idx = None
            for i, sid in enumerate(self.sensor_ids):
                if sid == self.selected_sensor_id:
                    sensor_idx = i
                    break
            if sensor_idx is not None:
                self.update_inspector(sensor_idx)

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
            self.save_state_to_history()
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

        # Check for unassigned regions
        unassigned_count = sum(1 for r in self.assignments.values() if r == 'unassigned')
        if unassigned_count > 0:
            reply = QMessageBox.question(
                self,
                "Unassigned Sensors",
                f"{unassigned_count} sensors are still unassigned to regions. Save anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Check for duplicate data_frame_indices (excluding -1)
        indices = [idx for idx in self.dataframe_indices.values() if idx != -1]
        duplicate_indices = [idx for idx in set(indices) if indices.count(idx) > 1]

        if duplicate_indices:
            duplicate_list = ', '.join(map(str, sorted(duplicate_indices)))
            # Build detailed message showing which sensors have duplicates
            dup_details = []
            for dup_idx in sorted(duplicate_indices):
                sensor_ids = [sid for sid, idx in self.dataframe_indices.items() if idx == dup_idx]
                dup_details.append(f"  Index {dup_idx}: sensors {', '.join(map(str, sensor_ids))}")

            detail_msg = "\n".join(dup_details)

            reply = QMessageBox.warning(
                self,
                "Duplicate Data Frame Indices",
                f"Warning: Duplicate data_frame_index values found:\n\n{detail_msg}\n\n"
                f"This may cause data conflicts. Save anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Check for unassigned data_frame_indices
        unassigned_indices_count = sum(1 for idx in self.dataframe_indices.values() if idx == -1)
        if unassigned_indices_count > 0:
            reply = QMessageBox.question(
                self,
                "Unassigned Data Frame Indices",
                f"{unassigned_indices_count} sensor(s) have unassigned data_frame_index (-1). Save anyway?",
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
            # Add region and data_frame_index columns to dataframe
            self.df['region'] = self.df['sensor_id'].map(self.assignments)
            self.df['data_frame_index'] = self.df['sensor_id'].map(self.dataframe_indices)

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

    def set_inspector_enabled(self, enabled):
        """Enable or disable inspector controls"""
        self.inspector_index_input.setEnabled(enabled)
        self.inspector_update_btn.setEnabled(enabled)
        self.inspector_unassign_btn.setEnabled(enabled)

    def update_inspector(self, sensor_idx):
        """Update inspector panel with sensor information"""
        if self.df is None or sensor_idx is None:
            self.set_inspector_enabled(False)
            self.inspector_sensor_id_label.setText("Sensor ID: --")
            self.inspector_position_label.setText("Position: --")
            self.inspector_region_label.setText("Region: --")
            self.inspector_index_input.clear()
            self.inspector_status_label.clear()
            self.selected_sensor_id = None
            return

        # Get sensor info
        sensor_id = self.sensor_ids[sensor_idx]
        position = self.sensor_positions[sensor_idx]
        region = self.assignments.get(sensor_id, 'unassigned')
        data_frame_index = self.dataframe_indices.get(sensor_id, -1)

        # Update labels
        self.inspector_sensor_id_label.setText(f"Sensor ID: {sensor_id}")
        self.inspector_position_label.setText(f"Position: ({position[0]:.1f}, {position[1]:.1f}) mm")
        region_name = REGIONS.get(region, {}).get('name', region)
        self.inspector_region_label.setText(f"Region: {region_name}")

        # Update index input
        self.inspector_index_input.setText(str(data_frame_index))

        # Check for duplicates and update status
        self.update_inspector_status(data_frame_index)

        # Enable controls
        self.set_inspector_enabled(True)
        self.selected_sensor_id = sensor_id

    def update_inspector_status(self, current_index):
        """Update inspector status label with validation info"""
        if current_index == -1:
            self.inspector_status_label.setText("Status: Unassigned")
            self.inspector_status_label.setStyleSheet("padding: 5px; background-color: #fff3cd; color: #856404;")
        else:
            # Check for duplicates
            duplicates = self.check_duplicate_index(current_index)
            if duplicates:
                # Filter out current sensor
                other_duplicates = [sid for sid in duplicates if sid != self.selected_sensor_id]
                if other_duplicates:
                    dup_str = ', '.join(map(str, other_duplicates))
                    self.inspector_status_label.setText(f"⚠ Warning: Duplicate! Also used by sensor(s): {dup_str}")
                    self.inspector_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; color: #721c24;")
                else:
                    self.inspector_status_label.setText("✓ Valid")
                    self.inspector_status_label.setStyleSheet("padding: 5px; background-color: #d4edda; color: #155724;")
            else:
                self.inspector_status_label.setText("✓ Valid")
                self.inspector_status_label.setStyleSheet("padding: 5px; background-color: #d4edda; color: #155724;")

    def check_duplicate_index(self, index):
        """Check if index is used by other sensors. Returns list of sensor_ids with this index"""
        if index == -1:
            return []

        duplicates = []
        for sensor_id, idx in self.dataframe_indices.items():
            if idx == index:
                duplicates.append(sensor_id)

        return duplicates

    def on_index_update_clicked(self):
        """Handle Update button click in inspector"""
        if self.selected_sensor_id is None:
            return

        # Get and validate input
        index_text = self.inspector_index_input.text().strip()
        if not index_text:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid index (-1 to 255)")
            return

        try:
            new_index = int(index_text)
            if new_index < -1 or new_index > 255:
                QMessageBox.warning(self, "Invalid Range", "Index must be between -1 and 255")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid integer")
            return

        # Update the index
        self.update_dataframe_index(self.selected_sensor_id, new_index)

    def on_set_unassigned_clicked(self):
        """Handle Set Unassigned button click"""
        if self.selected_sensor_id is None:
            return

        self.update_dataframe_index(self.selected_sensor_id, -1)

    def update_dataframe_index(self, sensor_id, new_index):
        """Update data_frame_index for a sensor with undo support"""
        # Save to history
        self.save_state_to_history()

        # Update index
        old_index = self.dataframe_indices.get(sensor_id, -1)
        self.dataframe_indices[sensor_id] = new_index

        # Update inspector display
        self.inspector_index_input.setText(str(new_index))
        self.update_inspector_status(new_index)

        # Update visual if unassigned status changed
        if (old_index == -1) != (new_index == -1):
            self.plot_sensors()

        # Update status
        self.status_label.setText(f"Sensor {sensor_id}: data_frame_index set to {new_index}")

    def save_state_to_history(self):
        """Save current state to history for undo"""
        self.history.append({
            'assignments': dict(self.assignments),
            'dataframe_indices': dict(self.dataframe_indices)
        })


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SensorAnnotationTool()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

