# Real-time Glove Visualization Plan

## 🎯 Goal
Build a real-time pressure visualization system for the JQ Glove that displays sensor data at 10-20 Hz while capturing data at ~200 Hz.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Serial Reader Thread                      │
│  - Continuously read from USB port (~200 Hz)                 │
│  - Parse packets (find delimiter, extract data)              │
│  - Combine packet pairs (0x01 + 0x02) into frames            │
│  - Push frames to thread-safe queue                          │
│  - Buffer management (drop old frames if queue full)         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Thread-safe Queue (max size: 50)
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                    Data Processing Layer                      │
│  - Extract latest frame from queue (10-20 Hz timer)          │
│  - Parse sensor values from frame bytes                      │
│  - Apply sensor-to-index mapping                             │
│  - Calculate per-region statistics                           │
│  - (Future) Convert ADC to pressure values                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Update Signal
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                    GUI Visualization Thread                   │
│  - Update hand pressure map (colored sensor dots)            │
│  - Update statistics display (per-finger pressure)           │
│  - (Optional) Real-time plot of pressure over time           │
│  - Handle user controls (pause/resume, save, settings)       │
└──────────────────────────────────────────────────────────────┘
```

---

## 📚 Library Selection

### Chosen: **PyQtGraph**

**Rationale:**
1. ⚡ **Performance:** Designed for real-time scientific visualization
   - Can handle 60+ Hz updates easily
   - Hardware-accelerated rendering with OpenGL option
   - Efficient data update without full redraw

2. 🧵 **Threading:** Qt's signal-slot mechanism perfect for multi-threaded serial I/O
   - `QThread` for serial reader
   - Thread-safe signals for data passing
   - Timer-based updates at controlled rate

3. 🎨 **Features:**
   - `ScatterPlotItem` for sensor dots (easy color/size updates)
   - `PlotWidget` for time-series data
   - Built-in controls (buttons, sliders, labels)
   - Layout management with Qt widgets

4. 🔧 **Flexibility:**
   - Can add controls panel easily
   - Multiple views (hand map + plots)
   - Easy to extend with new features

**Alternative considered:** Matplotlib with FuncAnimation
- ❌ Rejected because:
  - Slower for 162 sensor updates at 10-20 Hz
  - Blitting can be tricky with complex updates
  - Less suited for multi-threaded serial reading

---

## 📐 Visualization Layout

```
┌────────────────────────────────────────────────────────────┐
│  JQ Glove Real-time Pressure Monitor                       │
├────────────────────┬───────────────────────────────────────┤
│                    │  Control Panel                         │
│                    │  ┌─────────────────────────────────┐  │
│                    │  │ Port: /dev/cu.usbmodem...       │  │
│                    │  │ Status: ● Connected             │  │
│   Hand Pressure    │  │ FPS: 15 / Frame: 12345          │  │
│   Map (Main)       │  │                                 │  │
│                    │  │ [Start] [Stop] [Save]           │  │
│   - Colored dots   │  │                                 │  │
│     for sensors    │  │ Update Rate: [▓▓▓▓░░] 15 Hz    │  │
│   - Colorbar       │  │                                 │  │
│   - Hand outline   │  └─────────────────────────────────┘  │
│                    │                                        │
│                    │  Statistics                            │
│                    │  ┌─────────────────────────────────┐  │
│                    │  │ Thumb:  max=45  mean=23.5       │  │
│                    │  │ Index:  max=78  mean=42.1       │  │
│                    │  │ Middle: max=91  mean=56.3       │  │
│                    │  │ Ring:   max=34  mean=18.7       │  │
│                    │  │ Little: max=12  mean=6.2        │  │
│                    │  │ Palm:   max=123 mean=67.8       │  │
│                    │  └─────────────────────────────────┘  │
└────────────────────┴───────────────────────────────────────┘
```

**Optional Extensions:**
- Bottom panel: Time-series plot (pressure over time for selected sensors)
- Settings dialog: Port selection, update rate, color scheme

---

## 🔨 Implementation Steps

### Phase 1: Core Infrastructure (MVP)
1. **Set up PyQtGraph window**
   - Create `QApplication` and main window
   - Set up basic layout (left: plot area, right: controls)

2. **Create Serial Reader Thread**
   - Inherit from `QThread`
   - Implement serial port reading
   - Packet parsing (delimiter detection, frame assembly)
   - Emit signals with complete frames

3. **Data Queue Management**
   - Thread-safe queue (`Queue` from `queue` module)
   - Producer: Serial thread pushes frames
   - Consumer: Main thread pulls frames at controlled rate

4. **Basic Hand Visualization**
   - Use `ScatterPlotItem` for sensor dots
   - Define sensor positions (simplified hand layout)
   - Color mapping: value → color (hot colormap: 0=black, 255=white/yellow)

5. **Update Timer**
   - `QTimer` at 50-100ms intervals (10-20 Hz)
   - Pull latest frame from queue
   - Update scatter plot colors/sizes

### Phase 2: Enhanced Features
1. **Control Panel**
   - Start/Stop buttons
   - Connection status indicator
   - Frame counter and FPS display
   - Save data button

2. **Statistics Display**
   - Real-time text labels for each region
   - Max, mean, active sensor count per region

3. **Sensor Position Refinement**
   - Better hand outline drawing
   - More accurate sensor positions based on documentation

### Phase 3: Advanced Features (Future)
1. **Time-series Plot**
   - Show pressure history for selected sensors
   - Scrolling plot (last 5-10 seconds)

2. **Data Recording**
   - Save raw data to file during capture
   - Playback mode for recorded sessions

3. **LSL Integration**
   - Stream frames to Lab Streaming Layer
   - For integration with other systems

4. **Settings & Configuration**
   - Port selection dialog
   - Baudrate configuration
   - Color scheme options
   - Update rate slider

---

## 🗂️ File Structure

```
playground/
├── realtime_glove_viz.py          # Main application
├── serial_reader.py               # Serial reading thread
├── glove_parser.py                # Packet/frame parsing logic
├── sensor_mapping.py              # Sensor-to-index mapping
├── hand_visualizer.py             # PyQtGraph hand visualization
└── README.md                      # This file
```

---

## 🔧 Class Architecture

### 1. `SerialReaderThread(QThread)`
**Responsibilities:**
- Open serial port
- Continuous read loop
- Parse packets and combine into frames
- Emit `frame_ready` signal

**Signals:**
- `frame_ready(frame_data: list)` - New frame available
- `connection_status(connected: bool, message: str)` - Connection status
- `error_occurred(error_msg: str)` - Error handling

**Methods:**
- `__init__(port, baudrate)`
- `run()` - Main thread loop
- `stop()` - Graceful shutdown

---

### 2. `GloveParser`
**Responsibilities:**
- Find delimiter in byte stream
- Extract packet index, sensor type, payload
- Combine packet pairs into frames
- Extract sensor values from frame using `sensor_mapping.py`

**Methods:**
- `find_delimiter(data: bytes) -> int`
- `parse_packet(data: bytes) -> tuple`
- `combine_packets(pkt1: bytes, pkt2: bytes) -> list`
- `extract_sensor_values(frame: list) -> dict` (uses sensor_mapping module)

---

### 3. `HandVisualizer(QWidget)`
**Responsibilities:**
- Display hand outline
- Render sensor dots with colors
- Update visualization based on sensor data
- Handle colorbar

**Methods:**
- `__init__()`
- `setup_ui()` - Create plot items
- `update_sensors(sensor_values: dict)` - Update visualization
- `set_colormap(cmap_name: str)` - Change color scheme

---

### 4. `MainWindow(QMainWindow)`
**Responsibilities:**
- Overall application window
- Layout management
- Control panel
- Statistics display
- Coordinate between components

**Methods:**
- `__init__()`
- `setup_ui()` - Create layout
- `start_capture()` - Start serial reading
- `stop_capture()` - Stop serial reading
- `update_display()` - Timer callback for updates
- `update_statistics(sensor_values: dict)` - Update stats panel

---

## 📊 Data Flow

```
USB Serial Port
      ↓
SerialReaderThread.run()
      ↓ (continuous loop at ~200 Hz)
Parse bytes → Find delimiter → Combine packets
      ↓
Emit frame_ready(frame_data) signal
      ↓
MainWindow.on_frame_ready() slot
      ↓
Push to frame_queue (Queue with maxsize=50)
      ↓
QTimer.timeout (10-20 Hz)
      ↓
MainWindow.update_display()
      ↓
Pop from frame_queue
      ↓
GloveParser.extract_sensor_values()
      ↓
HandVisualizer.update_sensors()
      ↓
Display updated on screen
```

---

## ⚙️ Configuration Parameters

```python
# Serial Configuration
SERIAL_PORT = '/dev/cu.usbmodem57640302171'
BAUDRATE = 921600
TIMEOUT = 1.0

# Protocol
DELIMITER = bytes([0xAA, 0x55, 0x03, 0x99])
PACKET_INDEX_01 = 0x01  # 128 bytes payload
PACKET_INDEX_02 = 0x02  # 144 bytes payload
FRAME_SIZE = 272  # Total frame size (128 + 144 bytes)

# Sensor Mapping (imported from sensor_mapping.py)
# - Correct byte indices from documentation diagram
# - Little finger: indices [31, 30, 29, ...]
# - Ring finger: indices [28, 27, 26, ...]
# - Middle finger: indices [25, 24, 23, ...]
# - Index finger: indices [22, 21, 20, ...]
# - Thumb: indices [19, 18, 17, ...]
# - Palm: indices [207-129]
# - IMU: indices [256-271]

# Visualization
UPDATE_RATE_HZ = 15  # GUI update frequency
FRAME_QUEUE_SIZE = 50  # Buffer size
SENSOR_DOT_SIZE = 8  # Pixels
COLORMAP = 'hot'  # Color scheme

# Display
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
```

---

## 🐛 Error Handling

1. **Serial Connection Lost:**
   - Detect disconnection
   - Display error message
   - Attempt auto-reconnection (optional)
   - Allow manual reconnection

2. **Buffer Overflow:**
   - Drop old frames if queue is full
   - Display warning indicator
   - Log dropped frame count

3. **Parse Errors:**
   - Skip malformed packets
   - Continue with next valid packet
   - Log error count

4. **Performance Issues:**
   - Monitor actual update rate
   - Display FPS/frame counter
   - Warn if falling behind

---

## 🎨 Visualization Details

### Sensor Representation
- **Shape:** Circle (ScatterPlotItem)
- **Size:** Fixed (8-10 pixels) or scaled by pressure
- **Color:** Heat map (black → red → yellow → white)
  - 0: Black (no pressure)
  - 50: Dark red
  - 128: Red/Orange
  - 200: Yellow
  - 255: White/yellow

### Hand Outline
- Draw using `PlotDataItem` with connected lines
- Approximate hand shape: palm + 5 fingers
- Light gray/black outline

### Colorbar
- Horizontal or vertical bar
- Show value range (0-255 or converted pressure)
- Update min/max dynamically

---

## 🚀 MVP Implementation Checklist

### Minimum Viable Product (Phase 1)
- [ ] Create basic PyQtGraph window
- [ ] Implement SerialReaderThread
- [ ] Parse packets and combine into frames
- [ ] Queue management (producer-consumer)
- [ ] Draw hand outline
- [ ] Place sensor dots at approximate positions
- [ ] Color sensors based on data values
- [ ] Update at 10-20 Hz
- [ ] Display connection status
- [ ] Start/Stop buttons

**Estimated time:** 2-4 hours

### Nice-to-Have (Phase 2)
- [ ] Per-region statistics display
- [ ] FPS counter
- [ ] Save data button
- [ ] Better hand layout with accurate positions

**Estimated time:** 2-3 hours

---

## 📝 Testing Strategy

1. **Test with captured data first**
   - Load `.bin` file instead of serial port
   - Verify parsing and visualization
   - Check frame rate performance

2. **Test with live device**
   - Connect to glove
   - Press different fingers
   - Verify correct sensors light up
   - Check update rate (should be smooth at 15 Hz)

3. **Stress test**
   - Run for extended period (10+ minutes)
   - Monitor memory usage
   - Check for frame drops

---

## 🔮 Future Enhancements

1. **Multi-hand support** (if multiple gloves connected)
2. **Heatmap overlay** instead of discrete dots
3. **3D hand model** with pressure mapped to surface
4. **Gesture recognition** (detect hand poses)
5. **Pressure threshold alerts** (warn if exceeding safe limits)
6. **Export to video** (record visualization)
7. **Web interface** (view remotely via browser)

---

## 📚 Dependencies

```bash
pip install pyqtgraph PyQt5 pyserial numpy
```

**Versions:**
- Python >= 3.8
- PyQt5 >= 5.15
- pyqtgraph >= 0.12
- pyserial >= 3.5
- numpy >= 1.20

---

## ✅ Ready to Implement

This plan provides:
- ✓ Clear architecture with separation of concerns
- ✓ Detailed class design
- ✓ Specific implementation steps
- ✓ Performance considerations
- ✓ Error handling strategy
- ✓ Testing approach

**Next step:** Implement MVP (Phase 1) with core functionality!

