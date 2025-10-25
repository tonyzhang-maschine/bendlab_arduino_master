# 🚀 START HERE - JQ Glove Visualization Project

**Welcome!** This guide will get you oriented quickly.

---

## ⚡ **Quick Start (3 Steps)**

### 1. Run the Application
```bash
cd playground
../.venv/bin/python realtime_glove_viz.py
```

### 2. In the GUI
- Click **"Start"** button
- Watch statistics update
- Press glove fingers to test

### 3. Check Current Status
- Read **[STATUS.md](STATUS.md)** for known issues
- Main issue: Visualization dots stay black (Issue #1)

---

## 📖 **Documentation Map**

### **I want to...**

| Goal | Document to Read |
|------|------------------|
| **Understand current status** | [STATUS.md](STATUS.md) ⭐ |
| **Run the application** | [QUICK_START.md](QUICK_START.md) |
| **Find specific documentation** | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |
| **Understand the architecture** | [realtime_vis_plan.md](realtime_vis_plan.md) |
| **Get project overview** | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| **See hardware/protocol details** | [README.md](README.md) |

---

## 🎯 **Current Status at a Glance**

```
✅ Working (85% complete):
  - Serial communication
  - Packet parsing
  - GUI framework
  - Statistics display
  - Documentation

🔴 Not Working (needs fix):
  - Visualization colors (all dots black)
  
🟡 Minor Issues:
  - Sensor mapping cross-talk
  - Occasional GUI freezing
```

---

## 📁 **File Structure**

```
playground/
├── START_HERE.md              ← You are here
├── STATUS.md                  ← Current issues (⭐ READ THIS)
├── DOCUMENTATION_INDEX.md     ← Complete docs navigation
├── PROJECT_SUMMARY.md         ← Project overview
├── QUICK_START.md             ← Usage guide
├── README.md                  ← Technical reference
│
├── realtime_glove_viz.py      ← Main app (run this!)
├── hand_visualizer.py         ← Visualization widget
├── serial_reader.py           ← Serial thread
├── glove_parser.py            ← Packet parser
├── sensor_mapping.py          ← Sensor indices
│
├── test_compatibility.py      ← System test
├── test_app_minimal.py        ← Minimal test
│
└── archive/                   ← Legacy scripts
    └── README_ARCHIVE.md      ← Archive docs
```

---

## 🔧 **For Developers**

### First Time Setup
1. Read [STATUS.md](STATUS.md) - understand current state
2. Run `test_compatibility.py` - verify system
3. Run `realtime_glove_viz.py` - see it in action
4. Review [realtime_vis_plan.md](realtime_vis_plan.md) - understand design

### Debugging Issue #1 (Colors Not Updating)
**Location:** `hand_visualizer.py` line 203-224  
**Symptom:** All dots remain black  
**Evidence:** Statistics show values but colors don't change  

**Debug Steps:**
1. Add prints in `update_sensors()` to see if called
2. Check `value_to_color()` output
3. Verify `scatter.setData()` is refreshing plot
4. Test with manual color values

### Running Tests
```bash
# Full system test
python test_compatibility.py

# Minimal GUI test  
python test_app_minimal.py
```

---

## 📊 **Key Facts**

- **Device:** JQ20-XL-11 Left Hand Glove
- **Sensors:** 136 pressure sensors (not 162!)
- **Protocol:** 921600 bps, delimiter `AA 55 03 99`
- **Frame Size:** 272 bytes (packet 0x01 + 0x02)
- **Indices:** Not sequential! Use `sensor_mapping.py`
- **IMU Data:** Indices 256-271 (not yet decoded)

---

## 🎓 **Learning Path**

### Beginner
1. [QUICK_START.md](QUICK_START.md) - Learn how to run
2. [README.md](README.md) - Understand hardware
3. [STATUS.md](STATUS.md) - See current progress

### Intermediate
1. [realtime_vis_plan.md](realtime_vis_plan.md) - Architecture
2. `glove_parser.py` - Data parsing logic
3. `hand_visualizer.py` - Visualization code

### Advanced
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Full project context
2. `sensor_mapping.py` - Complete sensor mapping
3. [COMPATIBILITY_UPDATE.md](COMPATIBILITY_UPDATE.md) - Migration details

---

## ⚠️ **Known Issues**

### Issue #1: 🔴 CRITICAL - Visualization Not Working
- All sensor dots remain black
- Statistics show data is captured
- Color calculation may be broken
- **Priority:** HIGH

### Issue #2: 🟡 MINOR - Sensor Cross-talk
- Adjacent fingers may trigger each other
- Need empirical verification
- **Priority:** MEDIUM

### Issue #3: 🟡 INTERMITTENT - GUI Freezing
- Occasional freezing/flickering
- Possibly data saving related
- **Priority:** MEDIUM

**See [STATUS.md](STATUS.md) for details and debugging guides.**

---

## 🎯 **Next Actions**

### Immediate (This Session)
- [ ] Run the app and test with glove
- [ ] Read [STATUS.md](STATUS.md) completely
- [ ] Understand Issue #1 (visualization colors)

### Short-term (This Week)
- [ ] Debug visualization color update
- [ ] Test finger isolation to verify mapping
- [ ] Profile GUI performance

### Long-term (Future)
- [ ] Add data recording
- [ ] Implement playback mode
- [ ] Decode IMU data
- [ ] Add LSL streaming

---

## 💡 **Tips**

1. **Always check STATUS.md first** - it's the source of truth
2. **Use test scripts** - verify before debugging
3. **Documentation is comprehensive** - search before asking
4. **Archive folder** - old scripts for reference only
5. **Git history** - track changes and fixes

---

## 🆘 **Getting Help**

### Problem: App won't run
→ Check [QUICK_START.md](QUICK_START.md) "Troubleshooting"

### Problem: Don't understand architecture
→ Read [realtime_vis_plan.md](realtime_vis_plan.md)

### Problem: Colors not working
→ See [STATUS.md](STATUS.md) "Issue #1"

### Problem: Sensor values wrong
→ Check [sensor_mapping.py](sensor_mapping.py)

### Problem: Need API reference
→ Look at [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## ✅ **Checklist for Success**

Before working on the code:
- [ ] Read [STATUS.md](STATUS.md)
- [ ] Understand [realtime_vis_plan.md](realtime_vis_plan.md)
- [ ] Run `test_compatibility.py` successfully
- [ ] Have glove connected and powered on

Before committing changes:
- [ ] Run tests
- [ ] Update [STATUS.md](STATUS.md) if fixing issues
- [ ] Document any new issues found
- [ ] Update relevant documentation

---

**Ready to begin!** 🚀

Start with [STATUS.md](STATUS.md) to understand where we are.

