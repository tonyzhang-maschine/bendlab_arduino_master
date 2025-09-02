import time
import threading
import queue
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ProcessedData:
    timestamp: float
    raw_data: Any
    parsed_values: Optional[List[float]] = None
    channel_names: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class DataProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processing_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.input_queue = queue.Queue(maxsize=config.get('data', {}).get('buffer_size', 1000))
        self.output_queue = queue.Queue(maxsize=config.get('data', {}).get('buffer_size', 1000))
        self.process_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        self.is_running = False
        
        self.data_format = config.get('data', {}).get('format', 'ascii')
        self.delimiter = config.get('data', {}).get('delimiter', ',')
        self.channel_count = config.get('lsl', {}).get('channel_count', 6)
        
    def start(self):
        if self.is_running:
            logger.warning("Data processor already running")
            return
        
        self.stop_event.clear()
        self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processing_thread.start()
        self.is_running = True
        logger.info("Data processor started")
    
    def stop(self):
        if not self.is_running:
            return
        
        self.stop_event.set()
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        self.is_running = False
        logger.info("Data processor stopped")
    
    def _process_loop(self):
        while not self.stop_event.is_set():
            try:
                data_packet = self.input_queue.get(timeout=0.1)
                processed = self._process_data_packet(data_packet)
                if processed:
                    try:
                        self.output_queue.put_nowait(processed)
                        if self.process_callback:
                            self.process_callback(processed)
                    except queue.Full:
                        self.output_queue.get_nowait()
                        self.output_queue.put_nowait(processed)
                        
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                if self.error_callback:
                    self.error_callback(f"Processing error: {e}")
    
    def _process_data_packet(self, packet: Dict) -> Optional[ProcessedData]:
        try:
            timestamp = packet.get('timestamp', time.time())
            raw_data = packet.get('data')
            
            if not raw_data:
                return None
            
            processed = ProcessedData(
                timestamp=timestamp,
                raw_data=raw_data
            )
            
            if self.data_format == 'ascii':
                parsed = self._parse_ascii_data(raw_data)
                if parsed:
                    processed.parsed_values = parsed
                    processed.channel_names = [f"CH{i+1}" for i in range(len(parsed))]
            else:
                parsed = self._parse_binary_data(raw_data)
                if parsed:
                    processed.parsed_values = parsed
                    processed.channel_names = [f"CH{i+1}" for i in range(len(parsed))]
            
            processed.metadata = {
                'port': packet.get('port'),
                'processing_time': time.time() - timestamp
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process data packet: {e}")
            return None
    
    def _parse_ascii_data(self, data: str) -> Optional[List[float]]:
        try:
            data = data.strip()
            
            if not data:
                return None
            
            parts = data.split(self.delimiter)
            
            values = []
            for part in parts:
                try:
                    value = float(part.strip())
                    values.append(value)
                except ValueError:
                    continue
            
            if len(values) == 0:
                return None
            
            while len(values) < self.channel_count:
                values.append(0.0)
            
            return values[:self.channel_count]
            
        except Exception as e:
            logger.debug(f"Failed to parse ASCII data: {e}")
            return None
    
    def _parse_binary_data(self, data: bytes) -> Optional[List[float]]:
        try:
            if len(data) < 4:
                return None
            
            values = []
            offset = 0
            
            while offset + 4 <= len(data) and len(values) < self.channel_count:
                value = np.frombuffer(data[offset:offset+4], dtype=np.float32)[0]
                values.append(float(value))
                offset += 4
            
            while len(values) < self.channel_count:
                values.append(0.0)
            
            return values[:self.channel_count]
            
        except Exception as e:
            logger.debug(f"Failed to parse binary data: {e}")
            return None
    
    def add_data(self, data_packet: Dict) -> bool:
        try:
            self.input_queue.put_nowait(data_packet)
            return True
        except queue.Full:
            try:
                self.input_queue.get_nowait()
                self.input_queue.put_nowait(data_packet)
                return True
            except:
                return False
    
    def get_processed_data(self, timeout: float = 0.1) -> Optional[ProcessedData]:
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def flush_queues(self):
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
    
    def set_callbacks(self,
                      process_callback: Optional[Callable] = None,
                      error_callback: Optional[Callable] = None):
        if process_callback:
            self.process_callback = process_callback
        if error_callback:
            self.error_callback = error_callback
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()