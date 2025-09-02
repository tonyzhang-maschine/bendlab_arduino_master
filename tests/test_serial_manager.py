import pytest
import serial
from unittest.mock import Mock, patch, MagicMock
import time
import queue
from src.serial_manager import SerialManager, PortInfo

class TestPortInfo:
    def test_port_info_creation(self):
        port = PortInfo(
            port="/dev/ttyUSB0",
            description="Arduino Nano 33 BLE",
            hwid="USB VID:PID=2341:0043",
            vid=0x2341,
            pid=0x0043
        )
        assert port.port == "/dev/ttyUSB0"
        assert port.description == "Arduino Nano 33 BLE"
        assert port.vid == 0x2341
    
    def test_is_arduino_by_vid(self):
        port = PortInfo(
            port="/dev/ttyUSB0",
            description="Some Device",
            hwid="USB",
            vid=0x2341
        )
        assert port.is_arduino() == True
    
    def test_is_arduino_by_description(self):
        port = PortInfo(
            port="/dev/ttyUSB0",
            description="Arduino Nano 33 BLE",
            hwid="USB",
            vid=0x1234
        )
        assert port.is_arduino() == True
    
    def test_not_arduino(self):
        port = PortInfo(
            port="/dev/ttyUSB0",
            description="Generic USB Device",
            hwid="USB",
            vid=0x1234
        )
        assert port.is_arduino() == False

class TestSerialManager:
    @pytest.fixture
    def config(self):
        return {
            'serial': {
                'baudrate': 115200,
                'timeout': 1.0,
                'read_timeout': 0.1,
                'write_timeout': 0.5,
                'bytesize': 8,
                'parity': 'N',
                'stopbits': 1
            },
            'data': {
                'buffer_size': 100,
                'format': 'ascii',
                'delimiter': '\n',
                'encoding': 'utf-8'
            }
        }
    
    @pytest.fixture
    def serial_manager(self, config):
        return SerialManager(config)
    
    @patch('src.serial_manager.serial.tools.list_ports.comports')
    def test_list_available_ports(self, mock_comports):
        mock_port = Mock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "Test Device"
        mock_port.hwid = "USB"
        mock_port.vid = 0x1234
        mock_port.pid = 0x5678
        mock_port.serial_number = "12345"
        
        mock_comports.return_value = [mock_port]
        
        ports = SerialManager.list_available_ports()
        assert len(ports) == 1
        assert ports[0].port == "/dev/ttyUSB0"
        assert ports[0].description == "Test Device"
    
    @patch('src.serial_manager.serial.tools.list_ports.comports')
    def test_detect_arduino_ports(self, mock_comports):
        arduino_port = Mock()
        arduino_port.device = "/dev/ttyUSB0"
        arduino_port.description = "Arduino Nano 33 BLE"
        arduino_port.hwid = "USB"
        arduino_port.vid = 0x2341
        arduino_port.pid = 0x0043
        arduino_port.serial_number = "12345"
        
        other_port = Mock()
        other_port.device = "/dev/ttyUSB1"
        other_port.description = "Generic Device"
        other_port.hwid = "USB"
        other_port.vid = 0x1234
        other_port.pid = 0x5678
        other_port.serial_number = "67890"
        
        mock_comports.return_value = [arduino_port, other_port]
        
        arduino_ports = SerialManager.detect_arduino_ports()
        assert len(arduino_ports) == 1
        assert arduino_ports[0].port == "/dev/ttyUSB0"
    
    @patch('src.serial_manager.serial.Serial')
    def test_connect_success(self, mock_serial_class, serial_manager):
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial
        
        result = serial_manager.connect("/dev/ttyUSB0")
        
        assert result == True
        assert serial_manager.is_connected == True
        assert serial_manager.port == "/dev/ttyUSB0"
        mock_serial_class.assert_called_once()
        mock_serial.reset_input_buffer.assert_called_once()
        mock_serial.reset_output_buffer.assert_called_once()
    
    @patch('src.serial_manager.serial.Serial')
    def test_connect_failure(self, mock_serial_class, serial_manager):
        mock_serial_class.side_effect = serial.SerialException("Port not found")
        
        result = serial_manager.connect("/dev/ttyUSB0")
        
        assert result == False
        assert serial_manager.is_connected == False
    
    def test_disconnect(self, serial_manager):
        mock_serial = MagicMock()
        mock_serial.is_open = True
        serial_manager.serial_conn = mock_serial
        serial_manager.is_connected = True
        
        serial_manager.disconnect()
        
        assert serial_manager.is_connected == False
        assert serial_manager.serial_conn == None
        mock_serial.close.assert_called_once()
    
    def test_write_data_success(self, serial_manager):
        mock_serial = MagicMock()
        serial_manager.serial_conn = mock_serial
        serial_manager.is_connected = True
        
        result = serial_manager.write_data(b"test data")
        
        assert result == True
        mock_serial.write.assert_called_once_with(b"test data")
        mock_serial.flush.assert_called_once()
    
    def test_write_data_not_connected(self, serial_manager):
        serial_manager.is_connected = False
        
        result = serial_manager.write_data(b"test data")
        
        assert result == False
    
    def test_get_latest_data(self, serial_manager):
        test_data = {'timestamp': 123.456, 'data': 'test'}
        serial_manager.data_queue.put(test_data)
        
        result = serial_manager.get_latest_data(timeout=0.1)
        
        assert result == test_data
    
    def test_get_latest_data_empty(self, serial_manager):
        result = serial_manager.get_latest_data(timeout=0.01)
        assert result == None
    
    def test_flush_data_queue(self, serial_manager):
        serial_manager.data_queue.put({'data': 1})
        serial_manager.data_queue.put({'data': 2})
        serial_manager.data_queue.put({'data': 3})
        
        serial_manager.flush_data_queue()
        
        assert serial_manager.data_queue.empty()
    
    def test_set_callbacks(self, serial_manager):
        data_cb = Mock()
        error_cb = Mock()
        conn_cb = Mock()
        
        serial_manager.set_callbacks(
            data_callback=data_cb,
            error_callback=error_cb,
            connection_callback=conn_cb
        )
        
        assert serial_manager.data_callback == data_cb
        assert serial_manager.error_callback == error_cb
        assert serial_manager.connection_callback == conn_cb
    
    def test_process_data(self, serial_manager):
        data_cb = Mock()
        serial_manager.data_callback = data_cb
        serial_manager.port = "/dev/ttyUSB0"
        
        serial_manager._process_data("test data")
        
        assert not serial_manager.data_queue.empty()
        data_cb.assert_called_once()
        
        packet = serial_manager.data_queue.get()
        assert packet['data'] == "test data"
        assert packet['port'] == "/dev/ttyUSB0"
        assert 'timestamp' in packet