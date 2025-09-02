import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.output_handlers import CLIDisplay, LSLOutput, MockDataGenerator
from src.data_processor import ProcessedData

class TestCLIDisplay:
    @pytest.fixture
    def config(self):
        return {
            'display': {
                'buffer_display': 20,
                'show_timestamp': True,
                'show_raw': False,
                'update_rate': 10
            }
        }
    
    @pytest.fixture
    def cli_display(self, config):
        return CLIDisplay(config)
    
    def test_initialization(self, cli_display):
        assert cli_display.buffer_size == 20
        assert cli_display.show_timestamp == True
        assert cli_display.show_raw == False
        assert cli_display.update_rate == 10
        assert cli_display.data_buffer == []
        assert cli_display.stats['connection_status'] == 'Disconnected'
    
    def test_update_data(self, cli_display):
        data = ProcessedData(
            timestamp=123.456,
            raw_data="test",
            parsed_values=[1.0, 2.0, 3.0]
        )
        
        cli_display.update_data(data)
        
        assert len(cli_display.data_buffer) == 1
        assert cli_display.data_buffer[0] == data
        assert cli_display.stats['total_packets'] == 1
    
    def test_update_data_buffer_limit(self, cli_display):
        for i in range(50):
            data = ProcessedData(
                timestamp=123.456 + i,
                raw_data=f"test{i}"
            )
            cli_display.update_data(data)
        
        assert len(cli_display.data_buffer) <= cli_display.buffer_size * 2
        assert cli_display.stats['total_packets'] == 50
    
    def test_update_connection_status(self, cli_display):
        cli_display.update_connection_status(True, "/dev/ttyUSB0")
        
        assert cli_display.stats['connection_status'] == 'Connected'
        assert cli_display.stats['port'] == "/dev/ttyUSB0"
        
        cli_display.update_connection_status(False, "/dev/ttyUSB0")
        
        assert cli_display.stats['connection_status'] == 'Disconnected'
    
    def test_clear_buffer(self, cli_display):
        for i in range(5):
            data = ProcessedData(timestamp=123 + i, raw_data=f"test{i}")
            cli_display.update_data(data)
        
        cli_display.clear_buffer()
        
        assert cli_display.data_buffer == []
        assert cli_display.stats['total_packets'] == 0
        assert cli_display.stats['data_rate'] == 0.0

class TestLSLOutput:
    @pytest.fixture
    def config(self):
        return {
            'lsl': {
                'stream_name': 'TestStream',
                'stream_type': 'Test',
                'channel_count': 6,
                'nominal_rate': 100.0,
                'channel_format': 'float32',
                'source_id': 'test_001'
            }
        }
    
    @pytest.fixture
    def lsl_output(self, config):
        return LSLOutput(config)
    
    def test_initialization(self, lsl_output):
        assert lsl_output.outlet is None
        assert lsl_output.stream_info is None
        assert lsl_output.is_active == False
    
    @patch('src.output_handlers.StreamInfo')
    @patch('src.output_handlers.StreamOutlet')
    def test_start_success(self, mock_outlet_class, mock_info_class, config):
        lsl = LSLOutput(config)
        lsl.StreamInfo = mock_info_class
        lsl.StreamOutlet = mock_outlet_class
        lsl.lsl_available = True
        
        mock_info = Mock()
        mock_outlet = Mock()
        mock_info_class.return_value = mock_info
        mock_outlet_class.return_value = mock_outlet
        
        result = lsl.start()
        
        assert result == True
        assert lsl.is_active == True
        assert lsl.outlet == mock_outlet
        assert lsl.stream_info == mock_info
    
    def test_start_no_library(self, lsl_output):
        lsl_output.lsl_available = False
        
        result = lsl_output.start()
        
        assert result == False
        assert lsl_output.is_active == False
    
    def test_stop(self, lsl_output):
        lsl_output.outlet = Mock()
        lsl_output.stream_info = Mock()
        lsl_output.is_active = True
        
        lsl_output.stop()
        
        assert lsl_output.outlet is None
        assert lsl_output.stream_info is None
        assert lsl_output.is_active == False
    
    def test_send_data_success(self, lsl_output):
        mock_outlet = Mock()
        lsl_output.outlet = mock_outlet
        lsl_output.is_active = True
        
        data = ProcessedData(
            timestamp=123.456,
            raw_data="test",
            parsed_values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        )
        
        result = lsl_output.send_data(data)
        
        assert result == True
        mock_outlet.push_sample.assert_called_once_with(
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            123.456
        )
    
    def test_send_data_not_active(self, lsl_output):
        data = ProcessedData(
            timestamp=123.456,
            raw_data="test",
            parsed_values=[1.0, 2.0, 3.0]
        )
        
        result = lsl_output.send_data(data)
        
        assert result == False
    
    def test_send_data_no_parsed_values(self, lsl_output):
        lsl_output.outlet = Mock()
        lsl_output.is_active = True
        
        data = ProcessedData(
            timestamp=123.456,
            raw_data="test"
        )
        
        result = lsl_output.send_data(data)
        
        assert result == False

class TestMockDataGenerator:
    @pytest.fixture
    def config(self):
        return {
            'mock': {
                'data_rate': 100,
                'pattern': 'sine',
                'channels': 6,
                'amplitude': 100.0,
                'offset': 0.0
            }
        }
    
    @pytest.fixture
    def mock_generator(self, config):
        return MockDataGenerator(config)
    
    def test_initialization(self, mock_generator):
        assert mock_generator.is_running == False
        assert mock_generator.data_rate == 100
        assert mock_generator.pattern == 'sine'
        assert mock_generator.channels == 6
        assert mock_generator.amplitude == 100.0
        assert mock_generator.offset == 0.0
    
    def test_generate_sine_data(self, mock_generator):
        mock_generator.sample_counter = 0
        data = mock_generator._generate_sine_data()
        
        assert len(data) == 6
        assert all(isinstance(v, float) for v in data)
        assert all(-100 <= v <= 100 for v in data)
    
    def test_generate_random_data(self, mock_generator):
        data = mock_generator._generate_random_data()
        
        assert len(data) == 6
        assert all(isinstance(v, float) for v in data)
        assert all(-100 <= v <= 100 for v in data)
    
    def test_generate_constant_data(self, mock_generator):
        mock_generator.offset = 42.0
        data = mock_generator._generate_constant_data()
        
        assert len(data) == 6
        assert all(v == 42.0 for v in data)
    
    def test_generate_data_sine(self, mock_generator):
        mock_generator.pattern = 'sine'
        mock_generator.sample_counter = 0
        
        data = mock_generator._generate_data()
        
        assert 'timestamp' in data
        assert 'data' in data
        assert 'port' in data
        assert data['port'] == 'MOCK'
        assert ',' in data['data']
    
    def test_generate_data_random(self, mock_generator):
        mock_generator.pattern = 'random'
        
        data = mock_generator._generate_data()
        
        assert 'timestamp' in data
        assert 'data' in data
        assert data['port'] == 'MOCK'
    
    def test_generate_data_constant(self, mock_generator):
        mock_generator.pattern = 'constant'
        mock_generator.offset = 25.0
        
        data = mock_generator._generate_data()
        
        assert 'timestamp' in data
        assert 'data' in data
        assert data['port'] == 'MOCK'
        
        values = data['data'].split(',')
        assert len(values) == 6
        assert all(float(v) == 25.0 for v in values)
    
    @patch('threading.Thread')
    def test_start(self, mock_thread_class, mock_generator):
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread
        
        callback = Mock()
        mock_generator.start(callback)
        
        assert mock_generator.is_running == True
        assert mock_generator.data_callback == callback
        mock_thread.start.assert_called_once()
    
    def test_stop(self, mock_generator):
        mock_generator.is_running = True
        mock_generator.generation_thread = Mock()
        mock_generator.generation_thread.is_alive.return_value = True
        
        mock_generator.stop()
        
        assert mock_generator.is_running == False
        mock_generator.generation_thread.join.assert_called_once()