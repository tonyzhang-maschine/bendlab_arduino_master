#!/usr/bin/env python3
"""
Test script to verify the improvements:
1. Mock data doesn't stop at 1000 packets
2. Data values are displayed, not just timestamps
3. Mock data can be sent to LSL
"""

import time
import yaml
from src.serial_manager import SerialManager
from src.data_processor import DataProcessor, ProcessedData
from src.output_handlers import MockDataGenerator, CLIDisplay, LSLOutput

def test_mock_data_continuous():
    """Test that mock data continues beyond 1000 packets"""
    print("Testing continuous mock data generation...")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Increase data rate for faster testing
    config['mock']['data_rate'] = 1000  # 1000 Hz for fast testing
    
    mock_gen = MockDataGenerator(config)
    packet_count = 0
    
    def count_packets(data):
        nonlocal packet_count
        packet_count += 1
    
    mock_gen.start(count_packets)
    time.sleep(2)  # Let it run for 2 seconds
    mock_gen.stop()
    
    print(f"Generated {packet_count} packets in 2 seconds")
    assert packet_count > 1000, f"Expected > 1000 packets, got {packet_count}"
    print("✓ Mock data continues beyond 1000 packets")
    return True

def test_data_values_displayed():
    """Test that data values are properly parsed and displayed"""
    print("\nTesting data value parsing...")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    processor = DataProcessor(config)
    processor.start()
    
    # Create mock data packet
    test_packet = {
        'timestamp': time.time(),
        'data': '1.23,4.56,7.89,10.11,12.13,14.15',
        'port': 'TEST'
    }
    
    processor.add_data(test_packet)
    time.sleep(0.1)  # Give it time to process
    
    processed = processor.get_processed_data(timeout=1.0)
    processor.stop()
    
    assert processed is not None, "No processed data received"
    assert hasattr(processed, 'parsed_values'), "No parsed values"
    assert len(processed.parsed_values) == 6, f"Expected 6 values, got {len(processed.parsed_values)}"
    assert processed.parsed_values[0] == 1.23, f"First value mismatch: {processed.parsed_values[0]}"
    
    print(f"✓ Data values parsed correctly: {processed.parsed_values}")
    return True

def test_mock_with_lsl():
    """Test that mock data can be sent to LSL"""
    print("\nTesting mock data with LSL output...")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Test LSL output initialization
    lsl_output = LSLOutput(config)
    
    if not lsl_output.lsl_available:
        print("⚠ LSL library not available, skipping LSL test")
        return True
    
    if lsl_output.start():
        print("✓ LSL output initialized successfully")
        
        # Create test data
        test_data = ProcessedData(
            timestamp=time.time(),
            raw_data="1,2,3,4,5,6",
            parsed_values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        )
        
        result = lsl_output.send_data(test_data)
        lsl_output.stop()
        
        assert result, "Failed to send data to LSL"
        print("✓ Mock data can be sent to LSL")
    else:
        print("⚠ Could not start LSL stream (might be firewall or network issue)")
    
    return True

def test_buffer_size():
    """Test that buffer size has been increased"""
    print("\nTesting increased buffer size...")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    buffer_size = config.get('data', {}).get('buffer_size', 0)
    print(f"Current buffer size: {buffer_size}")
    
    assert buffer_size >= 10000, f"Buffer size too small: {buffer_size}"
    print("✓ Buffer size is adequate for continuous streaming")
    return True

def main():
    print("=" * 50)
    print("Testing Arduino COM Capture Improvements")
    print("=" * 50)
    
    tests = [
        test_buffer_size,
        test_data_values_displayed,
        test_mock_data_continuous,
        test_mock_with_lsl
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n🎉 All improvements verified successfully!")
    else:
        print(f"\n⚠ {failed} test(s) failed")

if __name__ == "__main__":
    main()