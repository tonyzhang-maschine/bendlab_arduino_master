"""
Serial Reader Thread - Continuous serial port reading with Qt signals

Reads data from USB serial port at ~200 Hz and emits complete frames
via Qt signals for thread-safe communication with GUI.
"""

import serial
import time
from PyQt5.QtCore import QThread, pyqtSignal
from glove_parser import GloveParser


class SerialReaderThread(QThread):
    # Qt signals for thread-safe communication
    frame_ready = pyqtSignal(object)  # Emits numpy array (frame data)
    connection_status = pyqtSignal(bool, str)  # connected, message
    error_occurred = pyqtSignal(str)  # error message
    stats_updated = pyqtSignal(dict)  # statistics
    
    def __init__(self, port: str, baudrate: int = 921600, timeout: float = 1.0):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.running = False
        self.serial_conn = None
        self.parser = GloveParser()
        self.stats_counter = 0
        
    def run(self):
        """Main thread loop - opens serial port and continuously reads data."""
        try:
            # Open serial connection
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connection_status.emit(True, f"Connected to {self.port}")
            self.running = True
            
            # Main reading loop
            while self.running:
                try:
                    # Read available data
                    if self.serial_conn.in_waiting > 0:
                        data = self.serial_conn.read(self.serial_conn.in_waiting)
                        
                        # Parse data and extract frames
                        frames = self.parser.add_data(data)
                        
                        # Emit each complete frame
                        for frame in frames:
                            self.frame_ready.emit(frame)
                        
                        # Emit statistics periodically (every 100 frames)
                        self.stats_counter += len(frames)
                        if self.stats_counter >= 100:
                            stats = self.parser.get_statistics()
                            self.stats_updated.emit(stats)
                            self.stats_counter = 0
                    else:
                        # Small sleep to prevent busy-waiting
                        time.sleep(0.001)
                        
                except serial.SerialException as e:
                    self.error_occurred.emit(f"Serial error: {str(e)}")
                    break
                except Exception as e:
                    self.error_occurred.emit(f"Unexpected error: {str(e)}")
                    
        except serial.SerialException as e:
            self.connection_status.emit(False, f"Failed to connect: {str(e)}")
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Fatal error: {str(e)}")
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the reading thread gracefully."""
        self.running = False
    
    def cleanup(self):
        """Clean up serial connection."""
        if self.serial_conn is not None:
            try:
                self.serial_conn.close()
                self.connection_status.emit(False, "Disconnected")
            except Exception as e:
                self.error_occurred.emit(f"Cleanup error: {str(e)}")
            finally:
                self.serial_conn = None



