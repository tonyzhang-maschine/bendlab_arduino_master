import pytest
import time
from unittest.mock import Mock, patch
from src.data_processor import DataProcessor, ProcessedData

class TestProcessedData:
    def test_processed_data_creation(self):
        data = ProcessedData(
            timestamp=123.456,
            raw_data="test,data",
            parsed_values=[1.0, 2.0, 3.0],
            channel_names=["CH1", "CH2", "CH3"],
            metadata={'port': '/dev/ttyUSB0'}
        )
        
        assert data.timestamp == 123.456
        assert data.raw_data == "test,data"
        assert data.parsed_values == [1.0, 2.0, 3.0]
        assert data.channel_names == ["CH1", "CH2", "CH3"]
        assert data.metadata['port'] == '/dev/ttyUSB0'

class TestDataProcessor:
    @pytest.fixture
    def config(self):
        return {
            'data': {
                'buffer_size': 100,
                'format': 'ascii',
                'delimiter': ','
            },
            'lsl': {
                'channel_count': 6
            }
        }
    
    @pytest.fixture
    def processor(self, config):
        return DataProcessor(config)
    
    def test_initialization(self, processor):
        assert processor.is_running == False
        assert processor.data_format == 'ascii'
        assert processor.delimiter == ','
        assert processor.channel_count == 6
    
    def test_start_stop(self, processor):
        processor.start()
        assert processor.is_running == True
        
        processor.stop()
        assert processor.is_running == False
    
    def test_parse_ascii_data_valid(self, processor):
        result = processor._parse_ascii_data("1.5,2.3,3.7,4.2,5.1,6.9")
        
        assert result is not None
        assert len(result) == 6
        assert result == [1.5, 2.3, 3.7, 4.2, 5.1, 6.9]
    
    def test_parse_ascii_data_partial(self, processor):
        result = processor._parse_ascii_data("1.5,2.3,3.7")
        
        assert result is not None
        assert len(result) == 6
        assert result[:3] == [1.5, 2.3, 3.7]
        assert result[3:] == [0.0, 0.0, 0.0]
    
    def test_parse_ascii_data_extra(self, processor):
        result = processor._parse_ascii_data("1,2,3,4,5,6,7,8,9")
        
        assert result is not None
        assert len(result) == 6
        assert result == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    
    def test_parse_ascii_data_invalid(self, processor):
        result = processor._parse_ascii_data("")
        assert result is None
        
        result = processor._parse_ascii_data("not,valid,data")
        assert result is None
    
    def test_parse_ascii_data_mixed(self, processor):
        result = processor._parse_ascii_data("1.5,invalid,3.7,4.2")
        
        assert result is not None
        assert len(result) == 6
        assert result[0] == 1.5
        assert result[1] == 3.7
        assert result[2] == 4.2
    
    def test_parse_binary_data_valid(self, processor):
        import numpy as np
        
        values = [1.5, 2.3, 3.7, 4.2, 5.1, 6.9]
        binary_data = b''.join([np.float32(v).tobytes() for v in values])
        
        result = processor._parse_binary_data(binary_data)
        
        assert result is not None
        assert len(result) == 6
        for i, v in enumerate(values):
            assert abs(result[i] - v) < 0.001
    
    def test_parse_binary_data_partial(self, processor):
        import numpy as np
        
        values = [1.5, 2.3, 3.7]
        binary_data = b''.join([np.float32(v).tobytes() for v in values])
        
        result = processor._parse_binary_data(binary_data)
        
        assert result is not None
        assert len(result) == 6
        assert result[3:] == [0.0, 0.0, 0.0]
    
    def test_parse_binary_data_invalid(self, processor):
        result = processor._parse_binary_data(b"")
        assert result is None
        
        result = processor._parse_binary_data(b"123")
        assert result is None
    
    def test_process_data_packet_ascii(self, processor):
        packet = {
            'timestamp': 123.456,
            'data': "1.5,2.3,3.7,4.2,5.1,6.9",
            'port': '/dev/ttyUSB0'
        }
        
        result = processor._process_data_packet(packet)
        
        assert result is not None
        assert result.timestamp == 123.456
        assert result.raw_data == "1.5,2.3,3.7,4.2,5.1,6.9"
        assert result.parsed_values == [1.5, 2.3, 3.7, 4.2, 5.1, 6.9]
        assert len(result.channel_names) == 6
        assert result.metadata['port'] == '/dev/ttyUSB0'
    
    def test_process_data_packet_binary(self, processor):
        import numpy as np
        
        processor.data_format = 'binary'
        values = [1.5, 2.3, 3.7, 4.2, 5.1, 6.9]
        binary_data = b''.join([np.float32(v).tobytes() for v in values])
        
        packet = {
            'timestamp': 123.456,
            'data': binary_data,
            'port': '/dev/ttyUSB0'
        }
        
        result = processor._process_data_packet(packet)
        
        assert result is not None
        assert result.timestamp == 123.456
        assert result.raw_data == binary_data
        assert len(result.parsed_values) == 6
    
    def test_process_data_packet_empty(self, processor):
        packet = {
            'timestamp': 123.456,
            'data': None,
            'port': '/dev/ttyUSB0'
        }
        
        result = processor._process_data_packet(packet)
        assert result is None
    
    def test_add_data(self, processor):
        packet = {'data': 'test'}
        
        result = processor.add_data(packet)
        assert result == True
        assert not processor.input_queue.empty()
    
    def test_add_data_full_queue(self, processor):
        for i in range(processor.input_queue.maxsize):
            processor.input_queue.put({'data': i})
        
        result = processor.add_data({'data': 'new'})
        assert result == True
    
    def test_get_processed_data(self, processor):
        data = ProcessedData(
            timestamp=123.456,
            raw_data="test"
        )
        processor.output_queue.put(data)
        
        result = processor.get_processed_data(timeout=0.1)
        assert result == data
    
    def test_get_processed_data_empty(self, processor):
        result = processor.get_processed_data(timeout=0.01)
        assert result is None
    
    def test_flush_queues(self, processor):
        processor.input_queue.put({'data': 1})
        processor.input_queue.put({'data': 2})
        processor.output_queue.put(ProcessedData(123, "test"))
        
        processor.flush_queues()
        
        assert processor.input_queue.empty()
        assert processor.output_queue.empty()
    
    def test_set_callbacks(self, processor):
        process_cb = Mock()
        error_cb = Mock()
        
        processor.set_callbacks(
            process_callback=process_cb,
            error_callback=error_cb
        )
        
        assert processor.process_callback == process_cb
        assert processor.error_callback == error_cb
    
    def test_process_loop_with_data(self, processor):
        packet = {
            'timestamp': 123.456,
            'data': "1.5,2.3,3.7,4.2,5.1,6.9",
            'port': '/dev/ttyUSB0'
        }
        processor.input_queue.put(packet)
        
        process_cb = Mock()
        processor.process_callback = process_cb
        
        # Start processor briefly
        processor.start()
        time.sleep(0.2)
        processor.stop()
        
        # Check results
        assert not processor.output_queue.empty()
        assert process_cb.called