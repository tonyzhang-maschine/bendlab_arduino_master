# Quick Start - Real-time Glove Visualization

## ✅ Status: READY TO USE

All components are now compatible with the updated sensor mapping (136 sensors with documented byte indices).

## 🚀 Run the Application

```bash
cd playground
../.venv/bin/python realtime_glove_viz.py
```

## 🧪 Test Compatibility First

```bash
cd playground
../.venv/bin/python test_compatibility.py
```

Expected output:
```
✅ All core components are compatible!
✅ Sensor mapping updated correctly (136 sensors)
✅ Parser uses documented indices
✅ Ready to test with real glove device
```

## 📊 What Changed

### Before (Broken):
- Used sequential indices 0-161 ❌
- Assumed 162 sensors ❌
- Generic finger/palm regions ❌

### After (Fixed):
- Uses documented byte indices (1-255) ✅
- Correct 136 sensors ✅
- Accurate regions from specification ✅

## 🎯 Expected Behavior

When you press glove fingers, you should see:
- **Thumb**: Indices [19, 18, 17, 3, 2, 1, 243, 242, 241, 227, 226, 225]
- **Index**: Indices [22, 21, 20, 6, 5, 4, 246, 245, 244, 230, 229, 228]
- **Middle**: Indices [25, 24, 23, 9, 8, 7, 249, 248, 247, 233, 232, 231]
- **Ring**: Indices [28, 27, 26, 12, 11, 10, 252, 251, 250, 236, 235, 234]
- **Little**: Indices [31, 30, 29, 15, 14, 13, 255, 254, 253, 239, 238, 237]
- **Palm**: Indices [207-129] (72 sensors with gaps)
- **Finger backs**: [238, 219, 216, 213, 210]

## 📝 Files Updated

1. **glove_parser.py** - Uses documented mapping
2. **hand_visualizer.py** - 136 sensors with correct indices
3. **realtime_glove_viz.py** - Updated statistics display
4. **requirements.txt** - Added PyQt5, pyqtgraph

## 🔧 Troubleshooting

### Issue: Import errors
```bash
# Install dependencies
cd /Users/zhuoruizhang/Desktop/projects/vibe_code_proj/arduino_bendlab_master
uv pip install --python .venv/bin/python3 -r requirements.txt
```

### Issue: "No module named 'PyQt5'"
```bash
uv pip install --python .venv/bin/python3 PyQt5 pyqtgraph
```

### Issue: Port not found
1. Check device: `ls /dev/cu.usbmodem*`
2. Update port in `realtime_glove_viz.py` line 17

## 📖 Documentation

- **README.md** - Full project overview
- **realtime_vis_plan.md** - Architecture details
- **COMPATIBILITY_UPDATE.md** - Detailed changes
- **README_REALTIME.md** - Original MVP guide

## ✨ Next Steps

1. **Run the app** with glove connected
2. **Press each finger** and verify correct sensors light up
3. **Check statistics panel** for max/mean values
4. **Adjust sensor positions** if needed in `hand_visualizer.py`
5. **Test for extended period** (10+ minutes)

---

**Ready to visualize! 🧤✨**

