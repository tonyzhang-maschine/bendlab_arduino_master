#!/usr/bin/env python3
"""
Real-time JQ Glove Visualization - Main Application

Displays real-time pressure data from JQ Glove device using PyQtGraph.
Captures data at ~200 Hz and visualizes at 10-20 Hz for smooth real-time display.
"""

import sys
import time
from queue import Queue, Full
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QGroupBox, 
                             QGridLayout, QTextEdit)
from PyQt5.QtCore import QTimer, Qt
import numpy as np

from hand_visualizer import HandVisualizer
from serial_reader import SerialReaderThread
from glove_parser import GloveParser


class MainWindow(QMainWindow):
    # Configuration
    SERIAL_PORT = '/dev/cu.usbmodem57640302171'
    BAUDRATE = 921600
    UPDATE_RATE_HZ = 15
    FRAME_QUEUE_SIZE = 50
    
    def __init__(self):
        super().__init__()
        
        # Data management
        self.frame_queue = Queue(maxsize=self.FRAME_QUEUE_SIZE)
        self.parser = GloveParser()
        self.serial_thread = None
        
        # Statistics
        self.frame_count = 0
        self.start_time = None
        self.last_update_time = time.time()
        self.dropped_frames = 0
        
        # Setup UI
        self.setup_ui()
        self.setup_timer()
        
        # Window properties
        self.setWindowTitle('JQ Glove Real-time Pressure Monitor')
        self.setGeometry(100, 100, 1200, 800)
    
    def setup_ui(self):
        """Create the main UI layout."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout (horizontal split)
        main_layout = QHBoxLayout(central_widget)
        
        # Left side: Hand visualization
        self.hand_viz = HandVisualizer()
        main_layout.addWidget(self.hand_viz, stretch=3)
        
        # Right side: Control panel and statistics
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Control panel
        control_group = self.create_control_panel()
        right_layout.addWidget(control_group)
        
        # Statistics panel
        stats_group = self.create_statistics_panel()
        right_layout.addWidget(stats_group)
        
        # Log panel
        log_group = self.create_log_panel()
        right_layout.addWidget(log_group)
        
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel, stretch=1)
    
    def create_control_panel(self) -> QGroupBox:
        """Create control panel with buttons and status."""
        group = QGroupBox("Control Panel")
        layout = QVBoxLayout()
        
        # Connection status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.status_label)
        
        # Port info
        self.port_label = QLabel(f"Port: {self.SERIAL_PORT}")
        layout.addWidget(self.port_label)
        
        # Frame counter
        self.frame_label = QLabel("Frames: 0 | FPS: 0.0")
        layout.addWidget(self.frame_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_capture)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Update rate info
        self.rate_label = QLabel(f"Update Rate: {self.UPDATE_RATE_HZ} Hz")
        layout.addWidget(self.rate_label)
        
        group.setLayout(layout)
        return group
    
    def create_statistics_panel(self) -> QGroupBox:
        """Create statistics panel showing per-region data."""
        group = QGroupBox("Sensor Statistics")
        layout = QGridLayout()
        
        # Region labels
        regions = [
            ('Thumb:', 'thumb'),
            ('Index:', 'index_finger'),
            ('Middle:', 'middle_finger'),
            ('Ring:', 'ring_finger'),
            ('Little:', 'little_finger'),
            ('Palm:', 'palm')
        ]
        
        self.region_labels = {}
        
        for i, (name, key) in enumerate(regions):
            label = QLabel(name)
            layout.addWidget(label, i, 0)
            
            value_label = QLabel("max=0  mean=0.0")
            value_label.setStyleSheet("font-family: monospace;")
            layout.addWidget(value_label, i, 1)
            
            self.region_labels[key] = value_label
        
        group.setLayout(layout)
        return group
    
    def create_log_panel(self) -> QGroupBox:
        """Create log panel for messages."""
        group = QGroupBox("Log")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
    
    def setup_timer(self):
        """Setup timer for periodic UI updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        interval_ms = int(1000 / self.UPDATE_RATE_HZ)
        self.update_timer.start(interval_ms)
    
    def start_capture(self):
        """Start serial data capture."""
        self.log_message("Starting capture...")
        
        # Create and start serial reader thread
        self.serial_thread = SerialReaderThread(self.SERIAL_PORT, self.BAUDRATE)
        
        # Connect signals
        self.serial_thread.frame_ready.connect(self.on_frame_ready)
        self.serial_thread.connection_status.connect(self.on_connection_status)
        self.serial_thread.error_occurred.connect(self.on_error)
        
        # Start thread
        self.serial_thread.start()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Reset statistics
        self.frame_count = 0
        self.dropped_frames = 0
        self.start_time = time.time()
    
    def stop_capture(self):
        """Stop serial data capture."""
        self.log_message("Stopping capture...")
        
        if self.serial_thread is not None:
            self.serial_thread.stop()
            self.serial_thread.wait()
            self.serial_thread = None
        
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Clear visualization
        self.hand_viz.clear()
    
    def on_frame_ready(self, frame_data):
        """Handle new frame from serial thread (called from serial thread)."""
        try:
            # Try to add frame to queue
            self.frame_queue.put_nowait(frame_data)
        except Full:
            # Queue is full, drop old frame
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.put_nowait(frame_data)
                self.dropped_frames += 1
            except:
                pass
    
    def on_connection_status(self, connected: bool, message: str):
        """Handle connection status updates."""
        self.log_message(f"Connection: {message}")
        
        if connected:
            self.status_label.setText("Status: ● Connected")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_label.setText("Status: ○ Disconnected")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
    
    def on_error(self, error_msg: str):
        """Handle error messages."""
        self.log_message(f"ERROR: {error_msg}")
    
    def update_display(self):
        """Update display with latest frame (called by timer at UPDATE_RATE_HZ)."""
        if self.frame_queue.empty():
            return
        
        # Get latest frame (discard intermediate frames for real-time display)
        frame_data = None
        frames_skipped = 0
        
        while not self.frame_queue.empty():
            try:
                frame_data = self.frame_queue.get_nowait()
                if frames_skipped > 0:
                    frames_skipped += 1
            except:
                break
        
        if frame_data is None:
            return
        
        # Update frame counter
        self.frame_count += 1
        
        # Extract sensor values using documented mapping
        sensor_info = self.parser.get_sensor_data(frame_data)
        if 'raw_frame' not in sensor_info:
            return
        
        # Update visualization with raw frame data
        self.hand_viz.update_sensors(frame_data)
        
        # Update statistics with region data
        self.update_statistics(sensor_info)
        
        # Update FPS display
        current_time = time.time()
        if self.start_time is not None:
            elapsed = current_time - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            self.frame_label.setText(f"Frames: {self.frame_count} | FPS: {fps:.1f}")
    
    def update_statistics(self, sensor_info: dict):
        """Update statistics panel with region data."""
        # Map UI region keys to sensor_mapping region keys
        region_mapping = {
            'thumb': 'thumb',
            'index_finger': 'index_finger',
            'middle_finger': 'middle_finger',
            'ring_finger': 'ring_finger',
            'little_finger': 'little_finger',
            'palm': 'palm'
        }
        
        for ui_key, sensor_key in region_mapping.items():
            if ui_key in self.region_labels and sensor_key in sensor_info:
                region_data = sensor_info[sensor_key]
                max_val = region_data.get('max', 0)
                mean_val = region_data.get('mean', 0)
                self.region_labels[ui_key].setText(f"max={max_val:3d}  mean={mean_val:5.1f}")
    
    def log_message(self, message: str):
        """Add message to log panel."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.serial_thread is not None:
            self.serial_thread.stop()
            self.serial_thread.wait()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

