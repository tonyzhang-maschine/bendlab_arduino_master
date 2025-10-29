# Performance Enhancement Roadmap

**Goal:** Achieve 100Hz+ sustained data acquisition with efficient storage and streaming capabilities

**Date:** October 28, 2025
**Version:** v1.6 → v2.0

---

## Current System Analysis

### Architecture
```
USB Serial (921600 bps, ~200 Hz raw packet rate)
    ↓
QThread (serial_reader.py) - Reads & parses packets
    ↓
Qt Signal/Slot - Thread-safe communication
    ↓
Main GUI Thread (realtime_glove_viz.py)
    ↓
Queue (10 frame limit) - Buffering
    ↓
Display Update (10 Hz) - Rendering
```

### Current Performance
- **Capture Rate:** ~76 Hz (limited by GIL and queue size)
- **Display Rate:** 10 Hz (intentional, smooth visualization)
- **Latency:** ~145ms (queue depth: 10 frames)
- **RAM Usage:** Low (<50 MB)

### Bottlenecks
1. **Python GIL** - Threads can't run true parallel CPU work
2. **Queue Size Limit** - 10 frames = dropped data at high rates
3. **Single-threaded parsing** - Parser in same thread as serial read
4. **No persistent storage** - Can't record sessions

---

## Recommended Solution: Python Multiprocessing

### Why Multiprocessing?
- ✅ **True parallelism** - Bypasses Python GIL
- ✅ **Process isolation** - Crash in one doesn't affect others
- ✅ **CPU affinity** - Can prioritize acquisition process
- ✅ **No rewrite needed** - Pure Python solution
- ✅ **Easier debugging** - Each process can be tested independently
- ✅ **Cross-platform** - Works on macOS, Linux, Windows

### Why NOT C/Rust? (Yet)
- ❌ **Premature optimization** - Python can handle 200 Hz easily
- ❌ **Development overhead** - Weeks of development time
- ❌ **I/O bound, not CPU bound** - USB read speed is the limit
- ❌ **Debugging complexity** - Harder to iterate

**Verdict:** Only consider C/Rust if Python multiprocessing can't meet requirements.

---

## Target Architecture

### Multi-Process Design
```
┌─────────────────────────────────────────────────────┐
│ Process 1: Data Acquisition (High Priority)        │
│ ├─ Serial reading at full 200+ Hz                  │
│ ├─ Frame parsing (272 bytes)                       │
│ ├─ Minimal processing (just parse)                 │
│ └─ Send to shared queue → [frame, timestamp]       │
└─────────────────────────────────────────────────────┘
                    ↓
        multiprocessing.Queue (large buffer)
                    ↓
        ┌─────────────┬─────────────────┐
        ↓             ↓                 ↓
┌─────────────┐ ┌──────────────┐ ┌────────────────┐
│ Process 2:  │ │ Process 3:   │ │ Process 4:     │
│ GUI/Display │ │ Data Logger  │ │ LSL Streamer   │
│ (10-20 Hz)  │ │ (200 Hz)     │ │ (200 Hz)       │
│             │ │              │ │                │
│ - Render    │ │ - HDF5 write │ │ - Publish LSL  │
│ - User I/O  │ │ - Async I/O  │ │ - Sync stream  │
└─────────────┘ └──────────────┘ └────────────────┘
```

### Benefits
- ✅ **Full 200 Hz capture** - No frame drops
- ✅ **Independent display** - GUI can't slow acquisition
- ✅ **Optional recording** - Doesn't affect display
- ✅ **Multiple consumers** - GUI + Logger + LSL simultaneously
- ✅ **Crash isolation** - Logger crash won't stop acquisition

---

## Data Storage Solutions

### Requirements
- **Data Rate:** 200 Hz × 272 bytes/frame = **54.4 KB/s** ≈ 3.3 MB/minute
- **Recording Duration:** Hours (typical HCI session)
- **File Size:** ~200 MB/hour (uncompressed), ~80 MB/hour (compressed)
- **Access Pattern:** Sequential write during capture, random read for analysis

### Option A: HDF5 ⭐ RECOMMENDED for Recording

**Why HDF5?**
- ✅ **Industry standard** for scientific/time-series data
- ✅ **Efficient chunked storage** - No RAM explosion
- ✅ **Built-in compression** - 2-3x smaller files (gzip level 1)
- ✅ **Fast random access** - Read any frame instantly
- ✅ **Self-documenting** - Stores metadata with data
- ✅ **Cross-platform** - Works everywhere
- ✅ **Mature Python support** - `h5py` library

**Implementation:**
```python
import h5py
import numpy as np

with h5py.File('session_2025-10-28_14-30-00.h5', 'w') as f:
    # Create dataset with chunked storage
    dset = f.create_dataset(
        'sensor_data',
        shape=(0, 272),        # Start with 0 rows
        maxshape=(None, 272),  # Unlimited rows
        dtype='uint8',
        chunks=(1000, 272),    # Write in 1000-frame chunks
        compression='gzip',
        compression_opts=1     # Fast compression
    )

    # Metadata
    f.attrs['sample_rate_hz'] = 200
    f.attrs['sensor_count'] = 161
    f.attrs['frame_size_bytes'] = 272
    f.attrs['timestamp_start'] = time.time()

    # Create timestamps dataset
    timestamps = f.create_dataset(
        'timestamps',
        shape=(0,),
        maxshape=(None,),
        dtype='float64',
        chunks=(1000,)
    )

    # Write in chunks (every 1000 frames = 5 seconds at 200 Hz)
    buffer = []
    ts_buffer = []
    for frame, ts in frame_stream:
        buffer.append(frame)
        ts_buffer.append(ts)

        if len(buffer) >= 1000:
            # Resize and write chunk
            idx = dset.shape[0]
            dset.resize((idx + 1000, 272))
            dset[idx:idx+1000] = np.array(buffer)

            timestamps.resize((idx + 1000,))
            timestamps[idx:idx+1000] = ts_buffer

            buffer.clear()
            ts_buffer.clear()
```

**File Structure:**
```
session_2025-10-28_14-30-00.h5
├── sensor_data [N × 272 uint8]     # Frame data
├── timestamps [N float64]           # Frame timestamps
├── sensor_mapping/
│   ├── sensor_ids [161 int]
│   ├── positions [161 × 2 float]   # x, y in mm
│   ├── regions [161 string]
│   └── data_frame_indices [161 int]
└── metadata (attributes)
    ├── sample_rate_hz: 200
    ├── sensor_count: 161
    ├── timestamp_start: 1730070600.0
    ├── duration_seconds: 3600
    └── device: "JQ20-XL-11"
```

**Performance:**
- Write speed: ~100-200 Hz sustained (non-blocking with chunking)
- Compression: ~2-3x reduction (gzip level 1)
- File size: ~80 MB/hour (compressed)
- Random access: <1ms to read any frame

---

### Option B: SQLite with Time-Series Extension

**Use Case:** When you need SQL queries or concurrent read access during recording.

```python
import sqlite3

conn = sqlite3.connect('glove_data.db')
conn.execute('''
    CREATE TABLE sensor_frames (
        timestamp REAL PRIMARY KEY,
        frame_data BLOB
    )
''')

# Write
conn.execute('INSERT INTO sensor_frames VALUES (?, ?)',
             (timestamp, frame.tobytes()))
```

**Pros:**
- ✅ Zero configuration (built into Python)
- ✅ SQL queries for analysis
- ✅ Can read while writing

**Cons:**
- ⚠️ Slower than HDF5 for streaming
- ⚠️ Not optimized for large binary arrays

**Verdict:** Use for metadata/logs, not primary data storage.

---

### Option C: Memory-Mapped Ring Buffer (Real-time Only)

**Use Case:** Ultra-low latency streaming with fixed memory footprint.

```python
import numpy as np
from multiprocessing import shared_memory

# 5-second ring buffer (200 Hz × 5s = 1000 frames)
buffer_size = 1000
shm = shared_memory.SharedMemory(
    create=True,
    size=buffer_size * 272
)
ring_buffer = np.ndarray(
    (buffer_size, 272),
    dtype=np.uint8,
    buffer=shm.buf
)

# Write with wraparound
write_idx = 0
ring_buffer[write_idx % buffer_size] = frame
write_idx += 1
```

**Pros:**
- ✅ Ultra-fast (zero copy)
- ✅ Fixed memory usage
- ✅ Process-shared

**Cons:**
- ❌ No persistence (lost on crash)
- ❌ Fixed size

**Verdict:** Use for real-time streaming between processes, not recording.

---

### NOT Recommended

#### Redis
- ❌ RAM-based storage (will fill memory quickly)
- ❌ External server overhead
- ❌ Designed for key-value, not time-series blobs

#### InfluxDB / TimescaleDB
- ❌ Designed for metrics (floats), not 272-byte binary frames
- ❌ External server complexity
- ❌ Overkill for local recording

#### gRPC
- ❌ Designed for network RPC, not local IPC
- ❌ More overhead than multiprocessing.Queue
- ❌ Unnecessary complexity

---

## Lab Streaming Layer (LSL) Integration

### Why LSL?
- ✅ **Standard protocol** in neuroscience/HCI research
- ✅ **Automatic time synchronization** with other streams
- ✅ **No custom IPC needed** - Well-tested infrastructure
- ✅ **Built-in recording** - LabRecorder tool
- ✅ **Cross-language** - MATLAB, Python, C++, Unity support
- ✅ **Network transparent** - Local or remote subscribers

### Architecture
```python
from pylsl import StreamInfo, StreamOutlet

# Create LSL stream
info = StreamInfo(
    name='JQGlove',
    type='Pressure',
    channel_count=161,        # One channel per sensor
    nominal_srate=200,        # 200 Hz
    channel_format='float32',
    source_id='JQ20-XL-11-Left'
)

# Add metadata
channels = info.desc().append_child('channels')
for i, sensor_id in enumerate(sensor_ids):
    ch = channels.append_child('channel')
    ch.append_child_value('label', f'Sensor_{sensor_id}')
    ch.append_child_value('region', sensor_regions[i])
    ch.append_child_value('position_x', positions[i][0])
    ch.append_child_value('position_y', positions[i][1])
    ch.append_child_value('unit', 'kPa')

outlet = StreamOutlet(info)

# Push samples at 200 Hz
for frame in frame_stream:
    sensor_values = extract_all_sensor_values(frame)
    pressure_values = calibration.adc_to_pressure(sensor_values, 'kPa')
    outlet.push_sample(pressure_values)  # Non-blocking
```

### Benefits
- ✅ Other tools can subscribe to stream (MATLAB, Python scripts)
- ✅ LabRecorder saves to XDF format (standard for multi-stream recording)
- ✅ Automatic timestamp synchronization across streams
- ✅ Can combine with EEG, eye tracking, etc.

---

## Implementation Roadmap

### Phase 1: Multiprocessing Refactor (Week 1) 🎯

**Goal:** Separate acquisition from display using multiprocessing.

**Tasks:**
1. **Extract serial reading to separate process**
   - Create `acquisition_process.py`
   - Move `SerialReaderThread` logic to process function
   - Use `multiprocessing.Queue` for communication

2. **Update main GUI to consume from queue**
   - Replace Qt signal connection with queue.get()
   - Non-blocking queue reads
   - Test frame delivery at 200 Hz

3. **Add process management**
   - Start/stop acquisition process from GUI
   - Handle process crashes gracefully
   - Monitor queue depth

4. **Profile and validate**
   - Verify 200 Hz sustained capture
   - Measure latency and jitter
   - Check for frame drops

**Deliverables:**
- `acquisition_process.py` - Standalone acquisition process
- Updated `realtime_glove_viz.py` - Process-based architecture
- Performance test script
- Documentation

**Success Criteria:**
- ✅ 200+ Hz sustained capture (no drops)
- ✅ <200ms total latency
- ✅ Display independent of capture rate
- ✅ Zero frame drops over 1-hour run

---

### Phase 2: HDF5 Recording (Week 2) 📊

**Goal:** Add persistent data recording without affecting real-time performance.

**Tasks:**
1. **Create logger process**
   - Separate process for file I/O
   - Reads from same queue as GUI
   - Chunked HDF5 writing

2. **Add recording UI controls**
   - Start/Stop recording button
   - Session name input
   - Recording indicator (red dot)
   - File size/duration display

3. **Implement chunked writing**
   - Buffer 1000 frames (5 seconds at 200 Hz)
   - Write chunks asynchronously
   - Add metadata and timestamps

4. **Add playback functionality**
   - Read HDF5 files
   - Replay at original rate or custom speed
   - Seek to any timepoint

**Deliverables:**
- `data_logger.py` - Recording process
- Recording UI in main window
- HDF5 file format documentation
- Playback tool

**Success Criteria:**
- ✅ Record full 200 Hz without frame drops
- ✅ <100 MB/hour file size (compressed)
- ✅ No impact on real-time display
- ✅ Can record for >2 hours continuously

---

### Phase 3: LSL Integration (Week 3) 🌐

**Goal:** Enable streaming to external tools and multi-modal recording.

**Tasks:**
1. **Install and test pylsl**
   - Add to dependencies
   - Test with LabRecorder
   - Verify on macOS/Linux/Windows

2. **Create LSL outlet**
   - Configure stream metadata
   - 161 channels (one per sensor)
   - Include sensor positions and regions

3. **Add LSL streaming option**
   - Toggle in GUI
   - Independent of visualization
   - Can run alongside recording

4. **Test with external tools**
   - LabRecorder (XDF recording)
   - MATLAB LSL client
   - Python LSL inlet example

**Deliverables:**
- LSL streaming in acquisition process
- Stream format documentation
- Example consumer scripts (Python, MATLAB)
- Multi-stream recording guide

**Success Criteria:**
- ✅ LSL stream visible in LabRecorder
- ✅ 200 Hz sustained streaming
- ✅ Correct timestamp synchronization
- ✅ Metadata accessible to subscribers

---

### Phase 4: Optimization & Production (Week 4) 🚀

**Goal:** Polish, optimize, and prepare for production use.

**Tasks:**
1. **Profile for bottlenecks**
   - cProfile analysis
   - Memory profiling
   - Identify slowest operations

2. **Tune parameters**
   - Queue sizes
   - Chunk sizes
   - Buffer sizes
   - Process priorities

3. **Cross-platform testing**
   - macOS, Linux, Windows
   - Different Python versions
   - Various hardware configs

4. **Documentation and examples**
   - User guide
   - API documentation
   - Tutorial notebooks
   - Example workflows

**Deliverables:**
- Performance report
- Tuning recommendations
- Complete documentation
- Example projects

**Success Criteria:**
- ✅ <1% frame drops over 8-hour session
- ✅ Works on all platforms
- ✅ Comprehensive documentation
- ✅ Ready for research use

---

## Expected Performance After Implementation

### Acquisition
- **Capture Rate:** 200+ Hz sustained ✅
- **Frame Drops:** <0.1% over long sessions ✅
- **CPU Usage:** <20% (acquisition process) ✅
- **Latency:** <100ms end-to-end ✅

### Recording
- **Write Speed:** 200 Hz to HDF5 ✅
- **File Size:** ~80 MB/hour (compressed) ✅
- **RAM Usage:** <100 MB (with buffering) ✅
- **Duration:** Limited by disk space only ✅

### Streaming (LSL)
- **Stream Rate:** 200 Hz ✅
- **Channels:** 161 (pressure values) ✅
- **Latency:** <50ms ✅
- **Subscribers:** Unlimited ✅

### Display
- **Update Rate:** 10-20 Hz (configurable) ✅
- **Responsiveness:** Smooth, no freezing ✅
- **CPU Usage:** <30% (GUI process) ✅

---

## Alternative Approaches Considered

### C/Rust Extension for Serial Reading
**Status:** Deferred

**When to reconsider:**
- Python multiprocessing can't sustain 200 Hz
- Profiling shows Python is CPU bottleneck (unlikely)
- Need >1000 Hz rate

**Effort:** 2-4 weeks development + ongoing maintenance

---

### ZeroMQ Instead of multiprocessing.Queue
**Status:** Not needed

**Reason:**
- multiprocessing.Queue handles 200 Hz easily (tested to 10kHz)
- ZeroMQ adds dependency and complexity
- No performance benefit for local IPC at this rate

**When to reconsider:**
- Need network streaming (but LSL is better for this)
- Multi-machine architecture
- Need pub/sub patterns

---

### Real-time OS / RT-Preempt Kernel
**Status:** Not needed

**Reason:**
- 200 Hz doesn't require hard real-time
- <100ms latency is acceptable for HCI applications
- Standard OS scheduling is sufficient

**When to reconsider:**
- Need <10ms latency guarantees
- Safety-critical applications
- Closed-loop control systems

---

## Risks and Mitigations

### Risk 1: USB Packet Loss
**Impact:** Frame drops at hardware level
**Likelihood:** Low (USB 2.0 has plenty of bandwidth)
**Mitigation:**
- Use high-quality USB cable
- Connect directly to computer (avoid hubs if possible)
- Monitor USB error rates

### Risk 2: Disk I/O Bottleneck
**Impact:** Recording can't keep up with 200 Hz
**Likelihood:** Low on SSD, Medium on HDD
**Mitigation:**
- Use SSD for recording
- Increase chunk size (write 5s chunks)
- Test with long recordings (>1 hour)
- Use compression (reduces I/O by 2-3x)

### Risk 3: Process Management Complexity
**Impact:** Harder to debug, more failure modes
**Likelihood:** Medium
**Mitigation:**
- Extensive error handling
- Process monitoring and auto-restart
- Logging from all processes
- Test failure scenarios

### Risk 4: Cross-Platform Issues
**Impact:** Works on one OS, fails on others
**Likelihood:** Medium (multiprocessing behavior varies)
**Mitigation:**
- Test on all platforms early
- Use cross-platform primitives (multiprocessing.Queue)
- Avoid platform-specific features
- Document OS-specific quirks

---

## Success Metrics

### Technical Metrics
- [ ] 200 Hz sustained capture for >8 hours
- [ ] <0.1% frame drops
- [ ] <100ms end-to-end latency
- [ ] <100 MB RAM usage
- [ ] Works on macOS, Linux, Windows

### Usability Metrics
- [ ] One-click start/stop recording
- [ ] Clear visual feedback (recording indicator)
- [ ] No GUI freezing during operation
- [ ] Easy to find recorded files
- [ ] Simple playback of recordings

### Integration Metrics
- [ ] LSL stream visible in LabRecorder
- [ ] Correct timestamp synchronization
- [ ] Can record alongside EEG/eye tracker
- [ ] Python/MATLAB can subscribe to stream

---

## References

### Documentation
- Python multiprocessing: https://docs.python.org/3/library/multiprocessing.html
- HDF5 format: https://www.hdfgroup.org/solutions/hdf5/
- h5py library: https://docs.h5py.org/
- Lab Streaming Layer: https://labstreaminglayer.org/
- pylsl: https://github.com/labstreaminglayer/liblsl-Python

### Similar Projects
- OpenBCI (EEG): Uses LSL for streaming
- Pupil Labs (eye tracking): HDF5 for recording
- Biosemi (EEG): ~2kHz sustained with Python

---

**Document Version:** 1.0
**Last Updated:** October 28, 2025
**Status:** Planning Phase
**Next Action:** Begin Phase 1 implementation
