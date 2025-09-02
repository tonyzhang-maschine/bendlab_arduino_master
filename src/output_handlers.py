import time
import threading
import logging
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
import numpy as np

logger = logging.getLogger(__name__)

class CLIDisplay:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('display', {})
        self.console = Console()
        self.buffer_size = self.config.get('buffer_display', 20)
        self.show_timestamp = self.config.get('show_timestamp', True)
        self.show_raw = self.config.get('show_raw', False)
        self.update_rate = self.config.get('update_rate', 10)
        
        self.data_buffer = []
        self.stats = {
            'total_packets': 0,
            'data_rate': 0.0,
            'last_update': time.time(),
            'connection_status': 'Disconnected',
            'port': 'N/A'
        }
        
        self.live_display: Optional[Live] = None
        self.display_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
    
    def start(self):
        self.stop_event.clear()
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        logger.info("CLI display started")
    
    def stop(self):
        self.stop_event.set()
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=2.0)
        if self.live_display:
            self.live_display.stop()
        logger.info("CLI display stopped")
    
    def _display_loop(self):
        with Live(self._generate_display(), refresh_per_second=self.update_rate, console=self.console) as live:
            self.live_display = live
            while not self.stop_event.is_set():
                live.update(self._generate_display())
                time.sleep(1.0 / self.update_rate)
    
    def _generate_display(self) -> Layout:
        layout = Layout()
        
        layout.split_column(
            Layout(self._create_header(), size=3),
            Layout(self._create_stats_panel(), size=6),
            Layout(self._create_data_panel())
        )
        
        return layout
    
    def _create_header(self) -> Panel:
        header_text = Text("Arduino BLE 33 Data Monitor", style="bold cyan", justify="center")
        return Panel(header_text, border_style="cyan")
    
    def _create_stats_panel(self) -> Panel:
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Label", style="bold yellow")
        stats_table.add_column("Value")
        
        status_style = "green" if self.stats['connection_status'] == 'Connected' else "red"
        stats_table.add_row("Status:", f"[{status_style}]{self.stats['connection_status']}[/{status_style}]")
        stats_table.add_row("Port:", str(self.stats['port']))
        stats_table.add_row("Total Packets:", str(self.stats['total_packets']))
        stats_table.add_row("Data Rate:", f"{self.stats['data_rate']:.1f} Hz")
        
        return Panel(stats_table, title="Connection Info", border_style="yellow")
    
    def _create_data_panel(self) -> Panel:
        if not self.data_buffer:
            return Panel("[dim]No data received yet...[/dim]", title="Data Stream", border_style="blue")
        
        data_table = Table(show_header=True, box=None)
        
        if self.show_timestamp:
            data_table.add_column("Timestamp", style="dim")
        
        # Always check for parsed values first to show channel data
        sample_data = self.data_buffer[-1] if self.data_buffer else None
        has_parsed_data = sample_data and hasattr(sample_data, 'parsed_values') and sample_data.parsed_values
        
        if has_parsed_data and not self.show_raw:
            # Show channel columns when we have parsed data
            for i in range(len(sample_data.parsed_values)):
                data_table.add_column(f"CH{i+1}", justify="right", style="green")
        else:
            # Fall back to raw data column
            data_table.add_column("Raw Data", style="cyan")
        
        for data in self.data_buffer[-self.buffer_size:]:
            row = []
            
            if self.show_timestamp:
                row.append(f"{data.timestamp:.3f}")
            
            if hasattr(data, 'parsed_values') and data.parsed_values and not self.show_raw:
                # Add parsed values
                for value in data.parsed_values:
                    row.append(f"{value:.2f}")
            else:
                # Add raw data
                raw_str = str(data.raw_data)[:100] if hasattr(data, 'raw_data') else "N/A"
                row.append(raw_str)
            
            if row:
                data_table.add_row(*row)
        
        return Panel(data_table, title="Data Stream", border_style="blue")
    
    def update_data(self, data):
        self.data_buffer.append(data)
        if len(self.data_buffer) > self.buffer_size * 2:
            self.data_buffer = self.data_buffer[-self.buffer_size:]
        
        self.stats['total_packets'] += 1
        
        current_time = time.time()
        time_diff = current_time - self.stats['last_update']
        if time_diff > 1.0:
            self.stats['data_rate'] = 1.0 / time_diff
            self.stats['last_update'] = current_time
    
    def update_connection_status(self, connected: bool, port: str = "N/A"):
        self.stats['connection_status'] = 'Connected' if connected else 'Disconnected'
        self.stats['port'] = port
    
    def clear_buffer(self):
        self.data_buffer.clear()
        self.stats['total_packets'] = 0
        self.stats['data_rate'] = 0.0

class LSLOutput:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('lsl', {})
        self.outlet = None
        self.stream_info = None
        self.is_active = False
        
        try:
            from pylsl import StreamInfo, StreamOutlet
            self.StreamInfo = StreamInfo
            self.StreamOutlet = StreamOutlet
            self.lsl_available = True
        except ImportError:
            logger.warning("LSL library not available. LSL output disabled.")
            self.lsl_available = False
    
    def start(self):
        if not self.lsl_available:
            logger.error("Cannot start LSL output: library not available")
            return False
        
        try:
            self.stream_info = self.StreamInfo(
                name=self.config.get('stream_name', 'ArduinoBLE33'),
                type=self.config.get('stream_type', 'Sensor'),
                channel_count=self.config.get('channel_count', 6),
                nominal_srate=self.config.get('nominal_rate', 100.0),
                channel_format=self.config.get('channel_format', 'float32'),
                source_id=self.config.get('source_id', 'arduino_ble33_001')
            )
            
            self.outlet = self.StreamOutlet(self.stream_info)
            self.is_active = True
            logger.info("LSL output stream started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start LSL stream: {e}")
            return False
    
    def stop(self):
        if self.outlet:
            self.outlet = None
            self.stream_info = None
            self.is_active = False
            logger.info("LSL output stream stopped")
    
    def send_data(self, data):
        if not self.is_active or not self.outlet:
            return False
        
        try:
            if hasattr(data, 'parsed_values') and data.parsed_values:
                self.outlet.push_sample(data.parsed_values, data.timestamp)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to send LSL data: {e}")
            return False

class MockDataGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('mock', {})
        self.is_running = False
        self.generation_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.data_callback = None
        
        self.data_rate = self.config.get('data_rate', 100)
        self.pattern = self.config.get('pattern', 'sine')
        self.channels = self.config.get('channels', 6)
        self.amplitude = self.config.get('amplitude', 100.0)
        self.offset = self.config.get('offset', 0.0)
        
        self.sample_counter = 0
    
    def start(self, callback):
        if self.is_running:
            return
        
        self.data_callback = callback
        self.stop_event.clear()
        self.generation_thread = threading.Thread(target=self._generate_loop, daemon=True)
        self.generation_thread.start()
        self.is_running = True
        logger.info("Mock data generator started")
    
    def stop(self):
        if not self.is_running:
            return
        
        self.stop_event.set()
        if self.generation_thread and self.generation_thread.is_alive():
            self.generation_thread.join(timeout=2.0)
        
        self.is_running = False
        logger.info("Mock data generator stopped")
    
    def _generate_loop(self):
        interval = 1.0 / self.data_rate
        
        while not self.stop_event.is_set():
            data = self._generate_data()
            if self.data_callback:
                self.data_callback(data)
            
            self.sample_counter += 1
            time.sleep(interval)
    
    def _generate_data(self) -> Dict:
        timestamp = time.time()
        
        if self.pattern == 'sine':
            values = self._generate_sine_data()
        elif self.pattern == 'random':
            values = self._generate_random_data()
        elif self.pattern == 'constant':
            values = self._generate_constant_data()
        else:
            values = [0.0] * self.channels
        
        data_str = ','.join([f"{v:.2f}" for v in values])
        
        return {
            'timestamp': timestamp,
            'data': data_str,
            'port': 'MOCK'
        }
    
    def _generate_sine_data(self) -> List[float]:
        t = self.sample_counter / self.data_rate
        values = []
        
        for i in range(self.channels):
            freq = 1.0 + i * 0.5
            phase = i * np.pi / 4
            value = self.amplitude * np.sin(2 * np.pi * freq * t + phase) + self.offset
            values.append(value)
        
        return values
    
    def _generate_random_data(self) -> List[float]:
        return [
            np.random.uniform(-self.amplitude, self.amplitude) + self.offset
            for _ in range(self.channels)
        ]
    
    def _generate_constant_data(self) -> List[float]:
        return [self.offset] * self.channels