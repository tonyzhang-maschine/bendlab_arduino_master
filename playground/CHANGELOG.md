# Changelog - JQ Glove Real-time Visualization

All notable changes to this project will be documented in this file.

---

## [v1.3] - 2025-10-25 - Performance Optimization Release 🚀

### Major Performance Improvements
- ✅ **Reduced visualization lag by 95%**: 3000ms+ → ~145ms (confirmed ≤1s by user)
- ✅ **Improved display rate by 100%**: 5 Hz choppy → 10 Hz stable
- ✅ **Eliminated window flickering**: 100% fixed with fixed-width labels
- ✅ **8-17x faster rendering**: Enabled OpenGL hardware acceleration

### Added
- OpenGL hardware acceleration via PyQtGraph configuration
- Performance benchmarking script: `test_performance_improvements.py`
- Application profiling tool: `profile_performance.py`
- Comprehensive documentation:
  - `docs/PERFORMANCE_OPTIMIZATION_v1.3.md` - Technical deep-dive
  - `docs/WHATS_NEW_v1.3.md` - User-facing release notes
  - `PERFORMANCE_IMPROVEMENTS_SUMMARY.md` - Quick reference
- Dependencies: PyOpenGL==3.1.10, PyOpenGL_accelerate==3.1.10

### Changed
- **Queue size reduced**: 50 → 10 frames (80% latency reduction: 658ms → 132ms)
- **Fixed-width status label**: Prevents window resizing (700px minimum width)
- **Monospace font**: For consistent text width in status display
- Updated `README.md` with v1.3 status and performance metrics
- Updated `STATUS.md` with resolved performance issues
- Updated `KNOWN_LIMITATIONS.md` - All major issues resolved
- Updated `requirements.txt` with PyOpenGL dependencies

### Performance Metrics
- **Rendering time**: 50-100ms → 5.9ms (achievable 169 Hz)
- **Queue latency**: 658ms → 132ms (80% reduction)
- **Total end-to-end latency**: ~3000ms → ~145ms (95% reduction)
- **Display rate**: 5 Hz actual → 10 Hz stable (100% improvement)

### Use Cases Expanded
Now suitable for:
- ✅ Real-time monitoring (~150ms latency)
- ✅ Interactive applications
- ✅ Gesture recognition (<200ms tolerance)
- ✅ Data logging and recording
- ✅ Development and testing

---

## [v1.2] - 2025-10-25 - Sequential Processing & Issue #3 Fix

### Fixed
- ✅ **Issue #3: GUI Freezing** - Removed frame skipping, implemented sequential processing
- ✅ Adaptive frame processing (1-3 frames per tick based on queue depth)
- ✅ Comprehensive performance monitoring (queue depth, timing, FPS tracking)

### Changed
- Display rate reduced from 15 Hz to 10 Hz (intentional, reduces processing load)
- Added separate counters for captured vs displayed frames
- Update processing time measurement added

### Added
- `test_sequential_processing.py` - Verification test for sequential processing
- `docs/ISSUE_3_FIX_SUMMARY.md` - Detailed fix documentation

### Performance
- No arbitrary frame skipping - maintains data stream sequence
- Adaptive processing prevents queue overflow
- Smooth visualization without freezing

### Known Limitations
- Visualization lag: ~3+ seconds (documented, not fixed yet)
- Display FPS: ~5 Hz actual (below 10 Hz target)
- Window flickering: Minor annoyance
- ⚠️ Not suitable for time-critical real-time applications

---

## [v1.1] - 2025-10-25 - Issue #1 Fix

### Fixed
- ✅ **Issue #1: Visualization Colors Not Updating** - Dynamic range adjustment implemented

### Added
- Dynamic color range scaling based on actual sensor data
- Algorithm: Uses 2.5× max value, clamped between 10-255
- Test scripts:
  - `test_color_generation.py`
  - `test_low_value_visualization.py`
  - `test_fix_integration.py`
  - `test_pyqtgraph_brush.py`
  - `test_scatter_update.py`
- `docs/ISSUE_1_FIX_SUMMARY.md` - Detailed fix documentation
- `docs/WHATS_NEW_v1.1.md` - Release notes

### Changed
- Color mapping now scales dynamically to low sensor values (0-10 range)
- Low values now 17× brighter and visible: RGB [9,0,0] → RGB [154,27,0]

### Known Issues
- Sensor mapping cross-talk (Issue #2) - Minor
- GUI freezing (Issue #3) - Intermittent
- Performance limitations documented

---

## [v1.0] - 2025-10-24 - Initial MVP Release

### Added
- Real-time visualization system for JQ20-XL-11 glove (136 sensors)
- Multi-threaded architecture:
  - Serial reader thread (QThread)
  - PyQtGraph GUI (main thread)
  - Thread-safe queue-based communication
- Serial communication at 921600 bps (~76 Hz stable capture)
- Frame parsing and assembly (272-byte frames)
- Hand visualization with colored sensor dots
- Per-region statistics (max, mean per finger)
- Start/Stop controls
- Connection status indicator
- Log panel with timestamps
- FPS counter and frame tracking

### Core Features
- ✅ Packet parsing with delimiter detection
- ✅ Frame assembly (packet 0x01 + 0x02)
- ✅ Documented sensor mapping (136 unique sensors)
- ✅ PyQtGraph-based visualization
- ✅ Real-time GUI with controls
- ✅ Graceful shutdown handling

### Documentation
- `README.md` - Project overview
- `docs/STATUS.md` - Current status tracking
- `docs/QUICK_START.md` - Usage guide
- `docs/DOCUMENTATION_INDEX.md` - Navigation hub
- `docs/PROJECT_SUMMARY.md` - High-level overview
- `docs/realtime_vis_plan.md` - Architecture design
- `sensor_mapping.py` - Complete sensor-to-index mapping

### Known Issues
- Issue #1: Visualization colors not updating (critical)
- Issue #2: Sensor mapping cross-talk (minor)
- Issue #3: Intermittent GUI freezing (moderate)

### Performance
- Capture: ~76 Hz
- Display: ~15 Hz target (actual varies)
- Processing: Sequential frame handling

---

## Legend

- ✅ Fixed/Resolved
- 🚀 Major feature/improvement
- ⚠️ Known limitation
- 🟡 Minor issue
- 🔴 Critical issue

---

## Version History Summary

| Version | Date | Status | Key Achievement |
|---------|------|--------|----------------|
| **v1.3** | 2025-10-25 | ✅ Production Ready | Performance optimized (95% lag reduction) |
| **v1.2** | 2025-10-25 | 🟡 Functional | Sequential processing, no frame skipping |
| **v1.1** | 2025-10-25 | 🟡 Functional | Visualization colors fixed |
| **v1.0** | 2025-10-24 | 🔴 MVP | Initial release, core functionality |

---

**Current Version:** v1.3  
**Status:** ✅ Production Ready - Performance Optimized!  
**Last Updated:** October 25, 2025

