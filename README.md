# Arduino BLE 33 COM Data Capture System

A robust Python application for capturing, displaying, and streaming serial data from Arduino BLE 33 devices connected via USB. Features real-time visualization, Lab Streaming Layer (LSL) integration, and mock data generation for testing.


```
IMPORTANT NOTICE:

In config.yaml, specify the correct delimiter for proper LSL data transfer

data:
  buffer_size: 1000  # Increased buffer size
  rolling_buffer_size: 1000  # Maximum points to keep in rolling queue
  format: 'ascii'  # Options: ascii, binary
  delimiter: ','  # Use ',' for MOCK data, use ' ' (space) for real bendlab data
  encoding: 'utf-8'

```


## Features

- **Automatic Arduino Detection**: Auto-detects Arduino devices connected via USB
- **Real-time CLI Display**: Live updating terminal interface with data visualization
- **Multiple Output Modes**:
  1. Display to CLI only
  2. Display to CLI and stream to LSL
  3. Mock data mode (for testing)
  4. Mock data mode with LSL output
- **Robust Error Handling**: Automatic reconnection with configurable retry attempts
- **Data Processing Pipeline**: Supports both ASCII and binary data formats
- **Highly Configurable**: YAML-based configuration for easy customization
- **Comprehensive Testing**: Full test suite with pytest

## Installation

### Prerequisites

- Python 3.11 or higher
- uv (for dependency management)

### Setup

1. **Install dependencies using uv:**
   ```bash
   uv pip install -r requirements.txt
   ```

## Quick Start

### Basic Usage

Run with interactive mode (prompts for port and output mode):
```bash
python arduino_com_capture.py
```

### Mock Data Testing

Test without hardware using mock data:
```bash
python arduino_com_capture.py --mock
```

### Command Line Options

```bash
python arduino_com_capture.py [OPTIONS]

Options:
  -c, --config PATH     Path to configuration file (default: config.yaml)
  -p, --port TEXT       COM port to use (e.g., COM3 or /dev/ttyUSB0)
  -m, --mode [1|2|3]    Output mode: 1=CLI, 2=CLI+LSL, 3=Mock
  --mock               Use mock data mode
  --help               Show help message
```

### Usage Examples

1. **Interactive mode** (prompts for everything):
   ```bash
   python arduino_com_capture.py
   ```

2. **Direct connection with CLI display**:
   ```bash
   python arduino_com_capture.py --port COM3 --mode 1
   ```

3. **Stream to LSL from real device**:
   ```bash
   python arduino_com_capture.py --port /dev/ttyUSB0 --mode 2
   ```

4. **Mock data for testing**:
   ```bash
   python arduino_com_capture.py --mock
   ```

5. **Mock data with LSL output** (for testing LSL pipeline):
   ```bash
   # Interactive: choose option 4
   python arduino_com_capture.py
   ```

## Project Structure

```
arduino_bendlab_master/
├── arduino_com_capture.py    # Main application entry point
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── src/                      # Source code modules
│   ├── __init__.py
│   ├── serial_manager.py     # Serial port communication
│   ├── data_processor.py     # Data parsing and processing
│   └── output_handlers.py    # Output handlers (CLI, LSL, Mock)
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_serial_manager.py
│   ├── test_data_processor.py
│   └── test_output_handlers.py
└── devlogs/                  # Development documentation
    └── 2025-09-02/
        └── arduino_com_capture_development_plan.md
```

## Architecture & Key Components

### System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Arduino BLE33  │────▶│  SerialManager   │────▶│  DataProcessor  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                           │
                              ▼                           ▼
                        ┌──────────┐              ┌──────────────┐
                        │   Mock   │              │   Queues     │
                        │Generator │              │ (Threaded)   │
                        └──────────┘              └──────────────┘
                                                          │
                                ┌─────────────────────────┴──────────────┐
                                ▼                                        ▼
                        ┌──────────────┐                       ┌──────────────┐
                        │  CLIDisplay  │                       │  LSLOutput   │
                        └──────────────┘                       └──────────────┘
```

### Core Modules

#### 1. **SerialManager** (`src/serial_manager.py`)

Handles all serial communication with the Arduino device.

**Key Classes:**
- `PortInfo`: Data class for port information
  - `is_arduino()`: Auto-detects Arduino devices by VID/PID
- `SerialManager`: Main serial communication handler

**Key Features:**
- Automatic port detection and Arduino identification
- Thread-safe data reading with queue management
- Automatic reconnection on connection loss (configurable attempts)
- Callbacks for data, errors, and connection status changes

**Key Methods:**
```python
SerialManager.list_available_ports()  # List all COM ports
SerialManager.detect_arduino_ports()  # Find Arduino devices
serial_manager.connect(port)          # Connect to specific port
serial_manager.disconnect()           # Close connection
serial_manager.write_data(bytes)      # Send data to device
serial_manager.get_latest_data()      # Get data from queue
```

#### 2. **DataProcessor** (`src/data_processor.py`)

Processes raw serial data into structured format.

**Key Classes:**
- `ProcessedData`: Data class for processed data packets
  - Contains: timestamp, raw_data, parsed_values, channel_names, metadata
- `DataProcessor`: Main data processing pipeline

**Key Features:**
- Supports ASCII (comma-delimited) and binary data formats
- Configurable channel count and delimiters
- Thread-safe processing with input/output queues
- Automatic padding/truncation to match channel count

**Key Methods:**
```python
processor.start()                    # Start processing thread
processor.stop()                     # Stop processing
processor.add_data(packet)          # Add raw data to queue
processor.get_processed_data()      # Get processed data
processor._parse_ascii_data(str)    # Parse CSV format
processor._parse_binary_data(bytes) # Parse binary format
```

#### 3. **Output Handlers** (`src/output_handlers.py`)

Contains all output modules for data display and streaming.

##### **CLIDisplay**

Rich terminal interface for real-time data visualization.

**Features:**
- Live updating display with Rich library
- Shows connection status, data rate, packet count
- Configurable buffer size and update rate
- Displays both timestamps and channel values

**Key Methods:**
```python
display.start()                        # Start display thread
display.stop()                         # Stop display
display.update_data(data)             # Add new data
display.update_connection_status()    # Update status
display.clear_buffer()                # Clear data buffer
```

##### **LSLOutput**

Lab Streaming Layer integration for data streaming.

**Features:**
- Creates LSL outlet for real-time streaming
- Configurable stream name, type, and channel count
- Supports float32 data format
- Compatible with LSL recording tools

**Key Methods:**
```python
lsl.start()              # Create LSL stream
lsl.stop()               # Close stream
lsl.send_data(data)     # Push data to stream
```

##### **MockDataGenerator**

Generates synthetic data for testing without hardware.

**Features:**
- Multiple data patterns: sine, random, constant
- Configurable data rate and channel count
- Adjustable amplitude and offset
- Mimics real Arduino data format

**Key Methods:**
```python
mock.start(callback)           # Start generation
mock.stop()                    # Stop generation
mock._generate_sine_data()    # Sine wave pattern
mock._generate_random_data()  # Random values
mock._generate_constant_data() # Constant values
```

### Data Flow

1. **Serial Data Reception**:
   - SerialManager reads bytes from serial port
   - Data queued in thread-safe buffer
   - Callbacks notify of new data

2. **Data Processing**:
   - DataProcessor dequeues raw data
   - Parses according to format (ASCII/binary)
   - Creates ProcessedData objects with timestamps

3. **Output Distribution**:
   - ProcessedData sent to active outputs
   - CLIDisplay updates terminal view
   - LSLOutput streams to network (if enabled)

### Configuration (`config.yaml`)

```yaml
serial:
  baudrate: 115200        # Serial communication speed
  timeout: 1.0           # Read timeout in seconds

data:
  buffer_size: 10000     # Queue size for data packets (increased for continuous streaming)
  format: 'ascii'        # Data format: ascii or binary
  delimiter: ','         # Delimiter for ASCII format
  channel_count: 6       # Expected number of channels

display:
  update_rate: 10        # Display refresh rate (Hz)
  show_timestamp: true   # Show timestamps in display
  buffer_display: 20     # Lines to show in terminal

lsl:
  stream_name: 'ArduinoBLE33'  # LSL stream identifier
  channel_count: 6              # Number of channels
  nominal_rate: 100.0           # Expected sample rate

mock:
  data_rate: 100         # Mock data generation rate (Hz)
  pattern: 'sine'        # Pattern: sine, random, constant
  channels: 6            # Number of channels to generate
  amplitude: 100.0       # Signal amplitude
```

## Data Format

### Expected Arduino Output

The system expects comma-separated values (CSV) format:
```
value1,value2,value3,value4,value5,value6\n
```

Example:
```
1.23,4.56,7.89,10.11,12.13,14.15
2.34,5.67,8.90,11.12,13.14,15.16
```

### Processed Data Structure

```python
ProcessedData:
  timestamp: float           # Unix timestamp
  raw_data: str/bytes       # Original data
  parsed_values: List[float] # Parsed channel values
  channel_names: List[str]  # Channel identifiers (CH1, CH2, ...)
  metadata: Dict            # Additional info (port, processing_time)
```

## Testing

Run the complete test suite:
```bash
python -m pytest tests/ -v
```

Run specific test modules:
```bash
python -m pytest tests/test_serial_manager.py -v
python -m pytest tests/test_data_processor.py -v
python -m pytest tests/test_output_handlers.py -v
```

## Development & Extension

### Adding New Output Handlers

1. Create new class in `src/output_handlers.py`:
```python
class CustomOutput:
    def __init__(self, config):
        # Initialize
    
    def start(self):
        # Start output
    
    def stop(self):
        # Stop output
    
    def send_data(self, data):
        # Handle processed data
```

2. Integrate in main application:
```python
# In arduino_com_capture.py
custom_output = CustomOutput(config_data)
custom_output.start()

# In on_processed_data callback
custom_output.send_data(processed_data)
```

### Modifying Data Processing

Edit `DataProcessor._parse_ascii_data()` or `_parse_binary_data()` in `src/data_processor.py` to handle different data formats.

### Custom Mock Data Patterns

Add new pattern generation in `MockDataGenerator`:
```python
def _generate_custom_pattern(self) -> List[float]:
    # Your pattern logic
    return values
```

## Troubleshooting

### Common Issues

1. **No ports detected**:
   - Check Arduino is connected via USB
   - Install Arduino drivers if needed
   - Check USB cable supports data (not power-only)

2. **Permission denied (Linux/Mac)**:
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

3. **LSL not working**:
   - Check firewall settings
   - Verify pylsl installation: `pip show pylsl`
   - Test with LSL viewer tools

4. **Data not displaying**:
   - Verify Arduino is sending data in correct format
   - Check baudrate matches Arduino sketch
   - Try mock mode to test display system

5. **Mock data stops updating**:
   - Buffer size increased to 10000 in config.yaml
   - Check system resources aren't exhausted

### Debug Mode

Enable debug logging by editing config.yaml:
```yaml
logging:
  level: 'DEBUG'  # Change from INFO to DEBUG
```

## Performance Considerations

- **Buffer Size**: Adjust `data.buffer_size` based on data rate
- **Update Rate**: Lower `display.update_rate` if CPU usage is high
- **Channel Count**: Match `lsl.channel_count` to actual data
- **Thread Safety**: All queues are thread-safe with automatic overflow handling
