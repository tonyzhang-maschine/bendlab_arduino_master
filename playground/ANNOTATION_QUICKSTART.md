# 🏷️ Sensor Annotation - Quick Start

## What You Have

**165 sensors** with precise coordinates in `glove_sensor_map_refined.csv`:
- **X range:** 21.5 → 135.4 mm (114mm wide)
- **Y range:** 97.0 → 248.0 mm (151mm tall)
- **Layout:** Y increases from palm (bottom) to fingertips (top)

**Coordinate hints:**
- High Y (~240-248mm) = **Finger tips**
- Mid Y (~150-200mm) = **Finger middle sections**  
- Low Y (~97-150mm) = **Palm area**

---

## 🚀 Launch the Tool

### Option 1: Quick Launch
```bash
cd playground
./run_annotation_tool.sh
```

### Option 2: Manual
```bash
cd playground
../.venv/bin/python annotate_sensors.py
```

---

## 📋 Annotation Workflow (10-15 minutes)

### Step 1: Load Data
1. Click **"Load CSV"** button
2. Select `glove_sensor_map_refined.csv`
3. You'll see 165 gray dots (all unassigned)

### Step 2: Annotate Fingers First
Start from **right to left** (assuming left-hand glove):

**Thumb (right side, X ~80-135mm):**
- Use **Lasso** mode
- Draw around thumb sensors (high Y values on right side)
- Click **Thumb** button → Sensors turn red

**Index Finger:**
- Lasso around next finger column
- Click **Index** button → Green

**Middle Finger:**
- Usually center, highest Y values
- Click **Middle** button → Blue

**Ring Finger:**
- Left of middle
- Click **Ring** button → Yellow

**Little Finger (left side, X ~21-45mm):**
- Leftmost sensors
- Click **Little** button → Purple

### Step 3: Annotate Palm
- Switch to **Rectangle** mode
- Select all remaining gray sensors
- Click **Palm** button → Cyan

### Step 4: Review & Save
1. Check **Statistics panel** - should total 165
2. Zoom in to verify no sensors missed
3. Click **"Save Annotated CSV"**
4. Save as `glove_sensor_map_annotated.csv`

---

## 🎨 Selection Mode Guide

| Mode | Best For | How To Use |
|------|----------|------------|
| **Rectangle** | Large areas (palm) | Click → Drag → Click |
| **Lasso** | Irregular shapes (fingers) | Click → Draw → Click |
| **Click (single)** | Individual sensors | Click sensor directly |
| **Click (multi)** | Scattered sensors | Click multiple, click again to deselect |

---

## ⚠️ Common Issues

### "I can't see sensor IDs"
- Only every 5th sensor shows ID (to reduce clutter)
- Zoom in for details
- Hover over sensors for info

### "Selection isn't working"
- Rectangle/Lasso: **Two clicks** required (start + finish)
- Check bottom status bar for instructions
- Try switching modes

### "I made a mistake"
- Click **"Undo"** button
- Or reselect sensors and reassign to different region
- Or **"Clear All Assignments"** to start over

### "Some sensors overlap"
- Normal! Just zoom in
- Use **Click (multi)** mode for precise selection
- Pan with right-click drag

---

## 💡 Pro Tips

1. **Zoom is your friend** - Don't try to annotate while zoomed out
2. **Start with easy fingers** - Little and thumb are usually clear
3. **Use Lasso for curves** - Better than rectangle for finger shapes
4. **Check statistics** - Should add up to 165 before saving
5. **Save early, save often** - Tool remembers assignments when reloading

---

## 📊 Expected Distribution

Your annotation will roughly look like:

```
Region          Sensors    Color
─────────────────────────────────
Thumb           15-25      🔴 Red
Index           15-25      🟢 Green
Middle          15-25      🔵 Blue
Ring            15-25      🟡 Yellow
Little          15-25      🟣 Purple
Palm            50-80      🔵 Cyan
─────────────────────────────────
TOTAL           165        
```

*Exact numbers depend on your glove design!*

---

## ✅ After Annotation

Once you save `glove_sensor_map_annotated.csv`:

### Validate
```bash
cd playground
../.venv/bin/python -c "
import pandas as pd
df = pd.read_csv('glove_sensor_map_annotated.csv')
print(df.groupby('region').size())
"
```

### Next: Integrate with Visualization
The annotated CSV can be used to:
- Update `hand_visualizer.py` with accurate sensor positions
- Create better finger/palm layouts
- Match visualization to actual glove anatomy

---

## 🎯 You're Ready!

Just run the tool and start clicking! The interface is intuitive and you can't really break anything (Undo is always available).

```bash
cd playground
./run_annotation_tool.sh
```

**Happy annotating! 🧤✨**

---

*For detailed documentation, see:*
- `ANNOTATION_GUIDE.md` - Complete usage guide
- `ANNOTATION_TOOL_SUMMARY.md` - Technical details
- `annotate_sensors.py` - Source code (well commented)

