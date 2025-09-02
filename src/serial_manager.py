import serial
import serial.tools.list_ports
import threading
import queue
import time
import logging
from typing import Optional, List, Dict, Callable, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PortInfo:
    port: str
    description: str
    hwid: str
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    
    def is_arduino(self) -> bool:
        arduino_vids = [0x2341, 0x2A03, 0x1B4F, 0x239A]
        arduino_keywords = ['Arduino', 'arduino', 'BLE', 'Nano 33']
        
        if self.vid and self.vid in arduino_vids:
            return True
        
        for keyword in arduino_keywords:
            if keyword.lower() in self.description.lower():
                return True
        
        return False

class SerialManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('serial', {})
        self.port: Optional[str] = None
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected: bool = False
        self.read_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.data_queue = queue.Queue(maxsize=config.get('data', {}).get('buffer_size', 1000))
        self.error_callback: Optional[Callable] = None
        self.data_callback: Optional[Callable] = None
        self.connection_callback: Optional[Callable] = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2.0
        
    @staticmethod
    def list_available_ports() -> List[PortInfo]:
        ports = []
        for port in serial.tools.list_ports.comports():
            info = PortInfo(
                port=port.device,
                description=port.description,
                hwid=port.hwid,
                vid=port.vid,
                pid=port.pid,
                serial_number=port.serial_number
            )
            ports.append(info)
        return ports
    
    @staticmethod
    def detect_arduino_ports() -> List[PortInfo]:
        all_ports = SerialManager.list_available_ports()
        arduino_ports = [port for port in all_ports if port.is_arduino()]
        return arduino_ports
    
    def connect(self, port: str) -> bool:
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.disconnect()
            
            self.port = port
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=self.config.get('baudrate', 115200),
                timeout=self.config.get('timeout', 1.0),
                write_timeout=self.config.get('write_timeout', 0.5),
                bytesize=self.config.get('bytesize', 8),
                parity=self.config.get('parity', 'N'),
                stopbits=self.config.get('stopbits', 1)
            )
            
            time.sleep(2)
            
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            
            self.is_connected = True
            self.reconnect_attempts = 0
            
            self.stop_event.clear()
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            logger.info(f"Successfully connected to {port}")
            if self.connection_callback:
                self.connection_callback(True, port)
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {port}: {e}")
            if self.error_callback:
                self.error_callback(f"Connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {port}: {e}")
            if self.error_callback:
                self.error_callback(f"Unexpected error: {e}")
            return False
    
    def disconnect(self):
        self.stop_event.set()
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
        
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                logger.info(f"Disconnected from {self.port}")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
        
        self.is_connected = False
        self.serial_conn = None
        
        if self.connection_callback:
            self.connection_callback(False, self.port)
    
    def _read_loop(self):
        logger.info("Starting read loop")
        buffer = ""
        
        while not self.stop_event.is_set():
            try:
                if self.serial_conn and self.serial_conn.is_open and self.serial_conn.in_waiting:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    
                    if self.config.get('format', 'ascii') == 'ascii':
                        try:
                            decoded = data.decode(self.config.get('encoding', 'utf-8'))
                            buffer += decoded
                            
                            delimiter = self.config.get('delimiter', '\n')
                            while delimiter in buffer:
                                line, buffer = buffer.split(delimiter, 1)
                                if line:
                                    self._process_data(line)
                        except UnicodeDecodeError as e:
                            logger.warning(f"Failed to decode data: {e}")
                            self._process_data(data)
                    else:
                        self._process_data(data)
                        
                else:
                    time.sleep(0.001)
                    
            except serial.SerialException as e:
                logger.error(f"Serial error in read loop: {e}")
                self.is_connected = False
                if self.error_callback:
                    self.error_callback(f"Connection lost: {e}")
                self._attempt_reconnect()
                break
            except Exception as e:
                logger.error(f"Unexpected error in read loop: {e}")
                if self.error_callback:
                    self.error_callback(f"Read error: {e}")
    
    def _process_data(self, data):
        timestamp = time.time()
        data_packet = {
            'timestamp': timestamp,
            'data': data,
            'port': self.port
        }
        
        try:
            self.data_queue.put_nowait(data_packet)
        except queue.Full:
            try:
                self.data_queue.get_nowait()
                self.data_queue.put_nowait(data_packet)
            except queue.Empty:
                pass
        
        if self.data_callback:
            self.data_callback(data_packet)
    
    def _attempt_reconnect(self):
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            return
        
        self.reconnect_attempts += 1
        logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        time.sleep(self.reconnect_delay)
        
        if self.port:
            if self.connect(self.port):
                logger.info("Reconnection successful")
            else:
                threading.Timer(self.reconnect_delay, self._attempt_reconnect).start()
    
    def write_data(self, data: bytes) -> bool:
        if not self.is_connected or not self.serial_conn:
            logger.warning("Cannot write data: not connected")
            return False
        
        try:
            self.serial_conn.write(data)
            self.serial_conn.flush()
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to write data: {e}")
            if self.error_callback:
                self.error_callback(f"Write failed: {e}")
            return False
    
    def get_latest_data(self, timeout: float = 0.1) -> Optional[Dict]:
        try:
            return self.data_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def flush_data_queue(self):
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except queue.Empty:
                break
    
    def set_callbacks(self, 
                      data_callback: Optional[Callable] = None,
                      error_callback: Optional[Callable] = None,
                      connection_callback: Optional[Callable] = None):
        if data_callback:
            self.data_callback = data_callback
        if error_callback:
            self.error_callback = error_callback
        if connection_callback:
            self.connection_callback = connection_callback
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()