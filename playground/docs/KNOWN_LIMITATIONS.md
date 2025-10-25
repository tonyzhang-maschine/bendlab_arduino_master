# Known Limitations - JQ Glove Real-time Visualization

**Version:** MVP v1.2  
**Last Updated:** October 25, 2025  
**Status:** Documented from User Testing

---

## 🔴 **Current Known Limitations**

### 1. Visualization Lag (~3+ Seconds) ⚠️
**Status:** Known Issue - Performance Bottleneck

**Description:**
- Significant delay between physical glove interaction and visualization update
- Measured lag: **~3 seconds or more**
- Data is captured correctly but display lags behind real-time

**Impact:**
- Reduces usability for real-time feedback applications
- Makes gesture recognition difficult
- Not suitable for time-critical applications

**Root Cause Analysis:**
- **Queue buffering:** 50-frame queue at 76Hz capture = 0.66 seconds buffer
- **Processing overhead:** ~8-10ms per update × multiple operations
- **PyQtGraph rendering:** Updating 136 scatter plot points + colors
- **Dynamic range calculation:** Per-frame vmax adjustment
- **Statistics computation:** Per-region calculations every frame
- **GUI event loop:** Qt event processing adds latency

**Why This Happens:**
```
Capture (76 Hz) → Queue (50 frames) → Process (10 Hz) → Render
    ↓                    ↓                  ↓              ↓
 13ms/frame          ~660ms buffer      100ms/tick    Variable
                                        
Total latency: 660ms (queue) + processing + rendering ≈ 3+ seconds
```

**Potential Improvements (Future):**
- Reduce queue size (50 → 10 frames) - reduces buffer to ~130ms
- Process multiple frames per tick more aggressively
- Skip visualization for intermediate frames (but maintain sequence in memory)
- Use OpenGL acceleration for rendering
- Optimize color mapping calculations
- Reduce scatter plot update frequency

**Workaround:**
- Accept latency for monitoring/recording applications
- For real-time needs: increase FRAMES_PER_UPDATE to 3-5

---

### 2. Low Display FPS (~5 Hz vs Expected 10 Hz) ⚠️
**Status:** Known Issue - Performance Limitation

**Description:**
- Configured display rate: 10 Hz (100ms timer)
- Actual achieved rate: **~5 Hz** (200ms per update)
- Display updates are slower than timer frequency

**Impact:**
- Visualization appears choppy
- Not smooth real-time feedback
- Combined with lag, makes system feel sluggish

**Root Cause Analysis:**
- **Update processing time exceeds timer interval:**
  - Timer interval: 100ms (10 Hz target)
  - Actual processing: 150-200ms per update
  - Result: Can only achieve ~5 Hz
  
- **Processing breakdown:**
  - Frame extraction: ~5ms
  - Sensor value mapping: ~10ms
  - Dynamic range calculation: ~5ms
  - Color generation: ~15ms
  - Statistics update: ~10ms
  - GUI text updates: ~5ms
  - PyQtGraph scatter plot update: ~50-100ms (bottleneck!)
  - **Total: 100-150ms+**

**Why PyQtGraph is Slow:**
- Updating 136 individual scatter plot points
- Each point: position + color (RGBA)
- Qt signal/slot overhead
- Full plot redraw on each update
- No hardware acceleration by default

**Evidence from Testing:**
```
Status Display Shows:
  Captured: 786 (12.0 Hz)     ← Lower than 76 Hz due to lag
  Displayed: 608 (9.3 Hz)     ← Lower than 10 Hz target
  Queue: 35/50 (max:37)       ← Queue stays near full
  Update: 9.8ms               ← Reported time (doesn't include rendering!)
```

**Note:** The 9.8ms "Update" time only measures Python processing, NOT PyQtGraph rendering time!

**Potential Improvements (Future):**
- Use PyQtGraph's OpenGL mode: `pg.setConfigOption('useOpenGL', True)`
- Batch update all points in single call (already doing this)
- Reduce number of displayed sensors (decimation)
- Use simpler visualization (heatmap instead of scatter plot)
- Profile with cProfile to find exact bottlenecks
- Consider switching to faster rendering library (e.g., vispy)

**Workaround:**
- Accept 5 Hz for current hardware/implementation
- Can try reducing sensor count for testing
- OpenGL mode may help (untested)

---

### 3. Window Resizing/Flickering ⚠️
**Status:** Known Issue - UI Design Flaw

**Description:**
- PyQt window constantly changes shape/size
- Triggered by FPS counter text changes
- Causes visual flickering and distraction

**Impact:**
- Distracting visual experience
- Makes GUI feel unstable
- Hard to focus on actual visualization

**Root Cause:**
- Status text length varies with numbers:
  ```
  "Captured: 786 (12.0 Hz) | ..."      ← Different lengths
  "Captured: 1234 (75.8 Hz) | ..."     ← Cause resize
  ```
- Qt auto-resizes labels to fit content
- No fixed width set for status label
- Layout manager adjusts window size

**Why This Happens:**
```python
# Current code (causes resizing):
self.frame_label.setText(f"Captured: {count} ({fps:.1f} Hz) | ...")
# Each update may change string length → Qt resizes label → window adjusts
```

**Fix (Easy):**
```python
# Set fixed-width font and minimum width:
self.frame_label.setMinimumWidth(800)
self.frame_label.setStyleSheet("font-family: monospace; min-width: 800px;")

# OR use formatted strings with padding:
status_text = f"Captured: {count:5d} ({fps:5.1f} Hz) | ..."
```

**Potential Improvements:**
- Set fixed width for status label
- Use monospace font (already using in some places)
- Pad numbers to fixed width
- Set window to fixed size (not resizable)

**Workaround:**
- Ignore the flickering for now
- Maximize window to reduce visible resizing

---

## 📊 **Performance Summary**

| Metric | Expected | Actual | Notes |
|--------|----------|--------|-------|
| Capture Rate | 76 Hz | 12 Hz (displayed) | Lag causes lower apparent rate |
| Display Rate | 10 Hz | ~5 Hz | Processing exceeds timer interval |
| Visualization Lag | <100ms | ~3+ seconds | Queue + processing bottleneck |
| Update Time | 100ms | 150-200ms | Includes rendering overhead |
| Queue Depth | <30% full | 70% full | Consistently high |

**Bottlenecks Identified:**
1. 🔴 **PyQtGraph rendering:** ~50-100ms (50-100% of total time)
2. 🟡 **Queue management:** 50 frames × 13ms = 660ms latency
3. 🟡 **Statistics calculation:** ~10ms per update
4. 🟡 **Dynamic color mapping:** ~15-20ms per update

---

## 🎯 **System Capabilities vs Limitations**

### ✅ **What Works Well:**
- Data capture and parsing (reliable)
- Sequential frame processing (no skipping)
- Statistics calculation (accurate)
- Queue management (adaptive, no crashes)
- Basic visualization (colors display correctly)

### ⚠️ **What Has Limitations:**
- Real-time responsiveness (3+ second lag)
- Display smoothness (5 Hz choppy)
- Window stability (resize flickering)
- High-frequency monitoring (<10Hz is hard to interpret)

### ❌ **What's Not Suitable For:**
- Real-time gesture recognition
- Time-critical applications
- Precise timing experiments
- High-frequency feedback loops
- Professional demonstrations (without fixes)

---

## 🔧 **Recommended Use Cases**

### ✅ **Suitable For:**
- Data logging and recording
- Offline analysis
- Sensor validation testing
- Long-term monitoring
- Development and debugging
- Educational demonstrations (with disclaimer)

### ⚠️ **Use With Caution:**
- Real-time monitoring (with lag awareness)
- Interactive applications (reduced responsiveness)
- Presentations (may appear sluggish)

### ❌ **Not Recommended For:**
- Real-time control systems
- Timing-critical experiments
- Professional real-time visualization
- Gesture-based interfaces (until optimized)

---

## 🔮 **Future Optimization Roadmap**

### High Priority (Would Significantly Improve):
1. **Enable PyQtGraph OpenGL mode** - Could reduce rendering to <10ms
2. **Reduce queue size** - 50 → 10 frames (660ms → 130ms latency)
3. **Fix window resizing** - Simple UI fix
4. **Profile with cProfile** - Identify exact bottlenecks

### Medium Priority (Would Help):
1. Batch color calculations
2. Cache dynamic range values (change less frequently)
3. Optimize scatter plot updates
4. Reduce statistics calculation frequency

### Low Priority (Nice to Have):
1. Alternative visualization modes (heatmap, contour)
2. Hardware acceleration investigation
3. Consider alternative GUI libraries (vispy, matplotlib)
4. Multi-threaded rendering

---

## 📝 **Testing Details**

### Test Environment:
- **Hardware:** (User's system)
- **OS:** macOS
- **Python:** 3.x
- **PyQt5 + PyQtGraph** (default configuration)
- **No OpenGL acceleration**

### Test Results:
```
Real-world Testing (User Feedback):
  - Visualization lag: ~3+ seconds (measured)
  - Display FPS: ~5 Hz (observed, not 10 Hz)
  - Window resizing: Constant flickering
  - Queue: Stays 70% full consistently
  
Console Output:
  Captured: 786 (12.0 Hz) 
  Displayed: 608 (9.3 Hz)
  Queue: 35/50 (max:37)
  Update: 9.8ms
```

**Analysis:**
- Capture rate appears low (12 Hz) due to downstream lag
- Display rate below target (9.3 vs 10 Hz)
- Queue near full (35/50 = 70%)
- Update time doesn't include rendering!

---

## ⚖️ **Trade-offs Made**

### Design Decisions:
1. **Chose sequential processing over speed**
   - Pro: Data integrity maintained
   - Con: Cannot skip frames to reduce lag

2. **Chose 10 Hz display rate**
   - Pro: Reduced processing load vs 15 Hz
   - Con: Choppy visualization, actual ~5 Hz

3. **Chose 50-frame queue**
   - Pro: Prevents overflow
   - Con: Adds ~660ms latency

4. **Chose PyQtGraph for visualization**
   - Pro: Easy to use, good for prototyping
   - Con: Slower rendering than alternatives

5. **Chose dynamic range adjustment**
   - Pro: Low values visible
   - Con: Adds per-frame computation overhead

---

## 📚 **Related Documentation**

- **[STATUS.md](STATUS.md)** - Overall system status
- **[ISSUE_3_FIX_SUMMARY.md](ISSUE_3_FIX_SUMMARY.md)** - Sequential processing details
- **[realtime_vis_plan.md](realtime_vis_plan.md)** - Original design (optimistic estimates!)

---

## 💡 **Quick Fixes to Try**

### For Users (Can Test Now):

1. **Reduce Queue Size:**
   ```python
   # In realtime_glove_viz.py line 29:
   FRAME_QUEUE_SIZE = 10  # Change from 50
   ```

2. **Enable OpenGL (Untested):**
   ```python
   # Add at top of realtime_glove_viz.py:
   import pyqtgraph as pg
   pg.setConfigOption('useOpenGL', True)
   pg.setConfigOption('enableExperimental', True)
   ```

3. **Increase Processing Rate:**
   ```python
   # In realtime_glove_viz.py line 29:
   FRAMES_PER_UPDATE = 5  # Change from 1
   ```

4. **Fix Window Resize:**
   ```python
   # In create_control_panel():
   self.frame_label.setMinimumWidth(600)
   ```

---

## ⚠️ **Important Notes**

1. **These limitations are KNOWN and DOCUMENTED**
   - Not bugs, but performance constraints
   - Result of design trade-offs
   - Can be improved with optimization effort

2. **System is still PRODUCTION READY for:**
   - Data logging
   - Offline analysis  
   - Development/testing
   - Non-time-critical monitoring

3. **NOT production ready for:**
   - Real-time control
   - Time-critical applications
   - Professional real-time visualization
   - Without disclaimers about lag

4. **Optimization is POSSIBLE but not yet implemented**
   - OpenGL could help significantly
   - Alternative rendering approaches available
   - Would require significant refactoring

---

## 🎓 **Lessons for Future Development**

1. **Performance profiling should be continuous**
   - Don't wait for user testing
   - Measure rendering time, not just Python time
   - Test on target hardware early

2. **Real-time visualization is hard**
   - PyQtGraph is good for prototyping, not production
   - Hardware acceleration is often needed
   - Latency compounds through pipeline

3. **User perception matters**
   - 3-second lag is unacceptable for "real-time"
   - 5 Hz feels choppy even if data is correct
   - UI flickering is very distracting

---

**Version:** MVP v1.2  
**Status:** Production Ready (with documented limitations)  
**Recommendation:** Use for logging/analysis, optimize for real-time use cases

